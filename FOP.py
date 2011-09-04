#!/usr/bin/env python3
""" FOP
    Filter Orderer and Preener
    Copyright (C) 2011 Michael

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>."""

# FOP version number
VERSION = 1.3

# Import the required modules
import os, re, subprocess, time
from urllib.parse import urlparse

# The following patterns are either taken from or based on Wladimir Palant's Adblock Plus source code
DOMAINPATTERN = re.compile(r"^([^\/\*\|\@\"\!]*?)##")
ELEMENTPATTERN = re.compile(r"^([^\/\*\|\@\"\!]*?)##([^{}]+)$")
OPTIONPATTERN = re.compile(r"^([^\/\"!]*?)\$(~?[\w\-]+(?:=[^,\s]+)?(?:,~?[\w\-]+(?:=[^,\s]+)?)*)$")
REPATTERN = re.compile(r"^(@@)?\/.*\/$")

# The following patterns match element tags and pseudo classes; "@" indicates either the beginning or end of a selector
SELECTORPATTERN = re.compile(r"(?<=([^\/\"\.\,\w\;\#\_\-\?\=\:\(\&\'\s]))(\s*[a-zA-Z]+\s*)((?=([^\"\\/;\w\d\-\,\'\.])))")
PSEUDOPATTERN = re.compile(r"((?<=[\:\]])|[>+]\s*[a-z]+)(\s*\:[a-zA-Z\-]{3,}\s*)(?=([\(\:\+\>\@]))")

# The following pattern identifies the sections of commit messages
COMMITPATTERN = re.compile(r"^(\w)\:\s(\((.+)\)\s|)(.*)$")

# The files with the following names should not be sorted, either because they have a special sorting system or because they are not filter files
IGNORE = ("CC-BY-SA.txt", "easytest.txt", "GPL.txt", "MPL.txt")

# The following is a tuple of the known Adblock Plus options
KNOWNOPTIONS =  ("collapse", "document", "donottrack", "elemhide",
                "image", "object", "object-subrequest", "other",
                "match-case", "script", "stylesheet", "subdocument",
                "third-party", "xbl", "xmlhttprequest")

def main (location = "."):
    # Print the name and version of the program
    print("=" * 44)
    print("FOP (Filter Orderer and Preener) version {version}".format(version=VERSION))
    print("=" * 44 + "\n")
    
    # Check for the presence of Mercurial and note whether any changes have been made by the user
    hgpresent = os.path.isdir("./.hg")
    if hgpresent:
        originaldifference = subprocess.check_output(["hg", "diff"])
        if originaldifference:
            print("The following changes to the repository have been recorded by Mercurial:")
            print(originaldifference.decode("utf-8"))
        else:
            print("Mercurial indicates that you have not made any changes to the repository.\n")
        
    # Find the names of all text files in the present directory, including sub-directories but not including hidden folders
    allfiles = []
    for path, directory, files in os.walk(location):
        for filename in files:
            address = os.path.join(path, filename)
            if "/." not in address:
                allfiles.append(address)
    
    # Process files as required
    for filename in allfiles:
        basename = os.path.basename(filename)
        (name, extension) = os.path.splitext(basename)
        # Sort all text files that are not blacklisted
        if extension == ".txt"  and basename not in IGNORE:
            print("Sorting {filename}...".format(filename=filename))
            fopsort(filename)
        # Delete unnecessary Mercurial backups as they are found
        if extension == ".orig":
            print("Deleting {filename}...".format(filename=filename))
            os.remove(filename)
    
    # Check whether the script is in a Mercurial repository and, if so, offer to commit the changes
    if hgpresent:
        if originaldifference:
            hgcommit(True)
        else:
            hgcommit(False)
    
    print("\nExiting...")

def fopsort (filename):
    filecontents = []
    # Read in the file given, removing blank lines
    with open(filename, "r") as inputfile:
        for line in inputfile:
            line = line.strip()
            if line != "":
                filecontents.append(line)
    
    outfile = []
    section = []
    newsectionline = 1
    filterlines = elementlines = 0
    # Work through the file, line by line
    for line in filecontents:
        # Ignore comments and, if applicable, sort the preceding section of filters and add them to the new version of the file
        if line.startswith("!") or line.startswith("[") and line.endswith("]") or line.startswith("%include"):
            if section:
                if elementlines > filterlines:
                    outfile.extend(sorted(section, key=lambda rule: re.sub(DOMAINPATTERN, "", rule)))
                else:
                    outfile.extend(sorted(section))
                section = []
            newsectionline = 1
            filterlines = elementlines = 0
            outfile.append(line)
        else:
            # Check the first ten lines of new sections to determine the filter type
            if newsectionline <= 10:
                if isglobalelement(line):
                    elementlines +=1
                else:
                    filterlines += 1
                newsectionline += 1
            
            # Neaten up filters
            if re.match(ELEMENTPATTERN, line):
                line = elementtidy(line)
            else:
                line = filtertidy(line)
            # Add the filter to the present section
            section.append(line)
    
    # At the end of the file, sort and add any remaining filters
    if section:
        if elementlines > filterlines:
            outfile.extend(sorted(section, key=lambda rule: re.sub(DOMAINPATTERN, "", rule)))
        else:
            outfile.extend(sorted(section))
    
    # Save the updated file
    outstream = "\n".join(outfile) + "\n"
    with open(filename, "w") as outputfile:
        outputfile.write(outstream)
        
def filtertidy (filterin):
    # Make regular filters entirely lower case
    filterin = filterin.lower()
    
    # If applicable, sort options
    optionsplit = re.search(OPTIONPATTERN, filterin)
    if optionsplit:
        # Split, clean and sort options
        filtertext = removeunnecessarywildcards(str(optionsplit.group(1)))
        optionlist = str(optionsplit.group(2)).split(",")
        
        domainlist = []
        newoptionlist = []
        for option in optionlist:
            if "domain=" in option:
                thislist = option.replace("domain=", "")
                thislist = thislist.split("|")
                domainlist.extend(thislist)
            else:
                # Warn if an unrecognised option is present
                if option.replace("~", "") not in KNOWNOPTIONS:
                    print("Warning: The option \"{option}\" used on the filter \"{problemfilter}\" is not recognised by FOP".format(option=option, problemfilter=filterin))
                newoptionlist.append(option)
        newoptionlist = sorted(newoptionlist, key=lambda option: option.strip("~"))
        
        # If applicable, sort domain restrictions and add the option to the end of the list
        if domainlist:
            domainoption = "domain=" + "|".join(sorted(domainlist, key=lambda domain: domain.strip("~")))
            newoptionlist.append(domainoption)
        
        # Join the options once more, separated by commas, add them to the filter and return it
        return filtertext + "$" + ",".join(newoptionlist)
    else:
        # Remove unnecessary asterisks and return the filter
        return removeunnecessarywildcards(filterin)

def elementtidy (rule):
    # Split the rule into the domains and the selector and set the former as lower case
    split = re.search(ELEMENTPATTERN, rule)
    domains = str(split.group(1)).lower()
    selector = str(split.group(2))

    # Order domain names alphabetically, ignoring exceptions
    if "," in domains:
        domainlist = sorted(domains.split(","), key=lambda domain: domain.strip("~"))
        domains = ",".join(domainlist)
    
    # Mark the beginning and the end of the selector in an unambiguous manner
    selector = "@" + selector + "@"
    # Make the tags lower case wherever possible
    for tag in re.finditer(SELECTORPATTERN, selector):
        bc = str(tag.group(1))
        tagname = str(tag.group(2))
        ac = str(tag.group(4))
        selector = selector.replace(bc + tagname + ac, bc + tagname.lower() + ac, 1)
    
    # Make pseudo classes lower case where possible
    for pseudo in re.finditer(PSEUDOPATTERN, selector):
        pseudoclass = str(pseudo.group(2))
        ac = str(pseudo.group(3))
        selector = selector.replace(pseudoclass + ac, pseudoclass.lower() + ac, 1)
    
    # Remove the markers for the beginning and end of the selector, join the rule once more and return it
    return domains + "##" + selector[1:-1]

def hgcommit (userchanges = True):
    print("\nStarting Mercurial commit procedure...\n")
    
    # Check for file changes and only continue if some have been made
    difference = subprocess.check_output(["hg", "diff"])
    if not difference:
        print("Mercurial has not recored any changes to the repository.")
        return
    print("The following changes to the repository have been recorded by Mercurial:")
    print(difference.decode("utf-8"))
    try:
        # Persistently request for a suitable comment
        while True:
            comment = str(input("Please enter a valid commit comment or quit:\n"))
            sections = re.search(COMMITPATTERN, comment)
            # Check whether the comment matches the required format
            if sections == None:
                print("The comment \"{comment}\" is not in the recognised format.".format(comment=comment))
            else:
                indicator = str(sections.group(1))
                message = str(sections.group(3))
                address = str(sections.group(4))
                
                if validurl(address):
                    if indicator == "M":
                        # The address is valid and the indicator is correct - leave the loop to commit the changes
                        break
                    elif (indicator == "A" or indicator == "P"):
                        if userchanges:
                            # The address is valid, the indicator is correct and the user made some modifications - leave the loop to commit the changes
                            break
                        else:
                            print("You have indicated that you have added or removed a rule, but no changes were initially noted by Mercurial.")
                    else:
                        print("Unrecognised indicator \"{character}\". Please select either \"A\", \"M\" or \"P\".".format(character=indicator))
                elif indicator == "M":
                    # Allow modifications to be made in an alternative format, but delay to allow the user time to abort if necessary
                    print("No recognised address in the comment \"{comment}\", but proceeding anyway in five seconds.".format(comment=comment))
                    time.sleep(5)
                    break
                else:
                    print("Unrecognised address \"{address}\".".format(address=address))
                
                print("")
    # Allow users to abort if necessary
    except (KeyboardInterrupt, SystemExit):
        print("\nCommit aborted.")
        return
    
    # When the comment has been accepted, commit the changes, checking for errors along the way and aborting if necessary
    print("Comment \"{comment}\" accepted.".format(comment=comment))
    commitreturn = subprocess.check_call(["hg", "commit", "-m", comment])
    if commitreturn != 0:
        print("Unexpected error with the command \"hg commit -m \"{comment}\"\".".format(comment=comment))
        print("Aborting commit procedure.")
        return
    print("\nConnecting to server. Please enter your password if required.")
    pullreturn = subprocess.check_call(["hg", "pull"])
    if pullreturn != 0:
        print("Unexpected error with the command \"hg pull\".")
        print("Aborting commit procedure.")
        return
    print("")
    pushreturn = subprocess.check_call(["hg", "push"])
    if pushreturn != 0:
        if pushreturn == 1:
            print("Nothing to push according to \"hg push\".")
        else:
            print("Unexpected error with the command \"hg pull\".")
        print("Aborting commit procedure.")
        return
        
    print("\nCompleted commit process succesfully.")
        
def isglobalelement (rule):
    # Check whether a rule is an element hiding rule and, if so, whether it is to be applied to all domains
    split = re.search(ELEMENTPATTERN, rule)
    if split:
        domainlist = str(split.group(1)).split(",")
        selector = str(split.group(2))
        # Check whether all domains are negations
        for domain in domainlist:
            if domain != "" and not domain.startswith("~"):
                return False
        return True
    else:
        return False

def validurl (url):
    addresspart = urlparse(url)
    # Require that an address has a scheme, domain name and path
    if addresspart.scheme and addresspart.netloc and addresspart.path:
        return True
    elif addresspart.scheme == "about" and addresspart.path:
        return True
    else:
        return False

def removeunnecessarywildcards (filtertext):
    whitelist = False
    if filtertext.startswith("@@"):
        whitelist = True
        filtertext = filtertext[2:]
    
    # Remove wildcards from the beginning of the filter
    while True:
        proposed = filtertext[1:]
        if filtertext.startswith("*") and len(proposed) > 1 and not proposed.startswith("|"):
            filtertext = proposed
        else:
            break
    # Remove wildcards from the end of the filter
    while True:
        proposed = filtertext[:-1]
        if filtertext.endswith("*") and len(proposed) > 1 and not re.match(REPATTERN, proposed) and not proposed.endswith("|"):
            filtertext = proposed
        else:
            break
    
    if whitelist:
        filtertext = "@@" + filtertext
    return filtertext
    
if __name__ == '__main__':
    main()
