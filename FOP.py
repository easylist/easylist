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
VERSION = 1.9

# Import the key modules
import os, re, subprocess, sys
# The following module is only available in Python 3; if it is not available, exit
try:
    from urllib.parse import urlparse
except ImportError:
    raise ImportError("The module urllib.parse is unable to be loaded; please upgrade to Python 3.")

# The following patterns are either taken from or based on Wladimir Palant's Adblock Plus source code
DOMAINPATTERN = re.compile(r"^([^\/\*\|\@\"\!]*?)##")
ELEMENTPATTERN = re.compile(r"^([^\/\*\|\@\"\!]*?)##([^{}]+)$")
OPTIONPATTERN = re.compile(r"^([^\/\"!]*?)\$(~?[\w\-]+(?:=[^,\s]+)?(?:,~?[\w\-]+(?:=[^,\s]+)?)*)$")

# The following patterns match element tags and pseudo classes; "@" indicates either the beginning or end of a selector
SELECTORPATTERN = re.compile(r"((?<=([@\+>\[\)]))|[>+#\.]\s*[\w]+\s+)(\s*[\w]+\s*)(?=([\[@\+>=\]\^\*\$\:]))")
PSEUDOPATTERN = re.compile(r"((?<=[\:\]])|[>+#\.\s]\s*[\w]+)(\s*\:[a-zA-Z\-]{3,}\s*)(?=([\(\:\+\>\@]))")

# The following pattern identifies the sections of commit messages
COMMITPATTERN = re.compile(r"^(\w)\:\s(\((.+)\)\s|)(.*)$")

# The files with the following names should not be sorted, either because they have a special sorting system or because they are not filter files
IGNORE = ("CC-BY-SA.txt", "easytest.txt", "GPL.txt", "MPL.txt")

# The following is a tuple of the known Adblock Plus options
KNOWNOPTIONS =  ("collapse", "document", "donottrack", "elemhide",
                "image", "object", "object-subrequest", "other",
                "match-case", "script", "stylesheet", "subdocument",
                "third-party", "xbl", "xmlhttprequest")
def start ():
    # Print the name and version of the program
    print("=" * 44)
    print("FOP (Filter Orderer and Preener) version {version}".format(version=VERSION))
    print("=" * 44)
    
    # Run the program in each of the locations specified, or the current working directory if no location is specified
    places = set(sys.argv[1:])
    if places:
        absoluteplaces = set()
        for place in places:
            # Make all of the references absolute before changing the working directory
            absoluteplaces.add(os.path.abspath(place))
        for place in absoluteplaces:
            main(place)
    else:
        main(os.getcwd())
    print("\nExiting...")

def main (location):
    # Move to the specified location if it exists
    if os.path.isdir(location):
        os.chdir(location)
    else:
        print("{location} does not exist or is not a folder.".format(location=location))
        return
    
    # Check for the presence of Mercurial and note whether any changes have been made by the user
    hgpresent = os.path.isdir("./.hg/")
    if hgpresent:
        originaldifference = True if subprocess.check_output(["hg", "diff"]) else False
    
    print("\nSorting the contents of {folder}".format(folder=location))
    for path, directory, files in os.walk("."):
        for filename in files:
            if "/." not in path:
                address = os.path.join(path, filename)
                (name, extension) = os.path.splitext(filename)
                # Sort all text files that are not blacklisted
                if extension == ".txt"  and filename not in IGNORE:
                    fopsort(address)
                # Delete unnecessary Mercurial backups as they are found
                if extension == ".orig":
                    os.remove(address)
    
    # If this is a Mercurial repository, offer to commit any changes
    if hgpresent:
        hgcommit(True) if originaldifference else hgcommit(False)

def fopsort (filename):
    # Read in the file given
    with open(filename, "r", encoding="utf-8", newline="\n") as inputfile:
        filecontents = inputfile.read().split("\n")
    if filecontents[:-1] == "":
        filecontents = filecontents[:-1]
    
    outfile = []
    section = set()
    newsectionline = 1
    CHECKLINES = 10
    filterlines = elementlines = 0
    # Work through the file line by line
    for line in filecontents:
        if line != "":
            # Ignore comments and, if applicable, sort the preceding section of filters and add them to the new version of the file
            if line[0] == "!" or line[0] == "[" and line[-1] == "]" or line[:8] == "%include":
                if section:
                    if elementlines > filterlines:
                        outfile.extend(sorted(section, key=lambda rule: re.sub(DOMAINPATTERN, "", rule)))
                    else:
                        outfile.extend(sorted(section))
                    section = set()
                newsectionline = 1
                filterlines = elementlines = 0
                outfile.append(line)
            else:
                # Neaten up filters, checking their type if necessary
                elementparts = re.search(ELEMENTPATTERN, line)
                if elementparts:
                    domains = elementparts.group(1).lower()
                    if newsectionline <= CHECKLINES:
                        if isglobalelement(domains):
                            elementlines += 1
                        else:
                            filterlines += 1
                    line = elementtidy(domains, elementparts.group(2))
                else:
                    if newsectionline <= CHECKLINES:
                        filterlines += 1
                    line = filtertidy(line)
                # Add the filter to the present section
                section.add(line)
                newsectionline += 1
    
    # At the end of the file, sort and add any remaining filters
    if section:
        if elementlines > filterlines:
            outfile.extend(sorted(section, key=lambda rule: re.sub(DOMAINPATTERN, "", rule)))
        else:
            outfile.extend(sorted(section))
    
    # Only save the updated file if required it has changed
    if outfile != filecontents:
        with open(filename, "w", encoding="utf-8", newline="\n") as outputfile:
            outputfile.write("\n".join(outfile) + "\n")
        
def filtertidy (filterin):
    # Make regular filters entirely lower case
    filterin = filterin.lower()
    
    # If applicable, sort options
    optionsplit = re.search(OPTIONPATTERN, filterin)
    if optionsplit:
        # Split, clean and sort options
        filtertext = removeunnecessarywildcards(optionsplit.group(1))
        optionlist = set(optionsplit.group(2).split(","))
        
        domainlist = set()
        domainentries = set()
        for option in optionlist:
            # Detect and separate domain options
            if option[0:7] == "domain=":
                domainlist.update(option[7:].split("|"))
                domainentries.add(option)
            elif option.strip("~") not in KNOWNOPTIONS:
                # Warn if an unrecognised option is present
                print("Warning: The option \"{option}\" used on the filter \"{problemfilter}\" is not recognised by FOP".format(option=option, problemfilter=filterin))
        # Sort all options other than domain alphabetically
        for option in domainentries:
            optionlist.remove(option)
        optionlist = sorted(optionlist, key=lambda option: option.strip("~"))
        
        # If applicable, sort domain restrictions and add the option to the end of the list
        if domainlist:
            optionlist.append("domain=" + "|".join(sorted(domainlist, key=lambda domain: domain.strip("~"))))
        
        # Add the options back to the filter and return it
        return filtertext + "$" + ",".join(optionlist)
    else:
        # Remove unnecessary asterisks and return the filter
        return removeunnecessarywildcards(filterin)

def elementtidy (domains, selector):
    # Order domain names alphabetically, ignoring exceptions
    if "," in domains:
        domains = ",".join(sorted(set(domains.split(",")), key=lambda domain: domain.strip("~")))
    # Mark the beginning and end of the selector in an unambiguous manner
    selector = "@" + selector + "@"
    # Make the tags lower case wherever possible
    for tag in re.finditer(SELECTORPATTERN, selector):
        tagname = tag.group(3)
        lowertagname = tagname.lower()
        if tagname != lowertagname:
            bc = tag.group(2)
            if bc == None:
                bc = tag.group(1)
            ac = tag.group(4)
            selector = selector.replace(bc + tagname + ac, bc + lowertagname + ac, 1)
    # Make pseudo classes lower case where possible
    for pseudo in re.finditer(PSEUDOPATTERN, selector):
        pseudoclass = pseudo.group(2)
        lowerpseudoclass = pseudoclass.lower()
        if pseudoclass != lowerpseudoclass:
            ac = pseudo.group(3)
            selector = selector.replace(pseudoclass + ac, lowerpseudoclass + ac, 1)
    # Remove the markers for the beginning and end of the selector, join the rule once more and return it
    return domains + "##" + selector[1:-1]

def hgcommit (userchanges):
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
                indicator = sections.group(1)
                if indicator == "M":
                    # Allow modification comments to have practically any format
                    break
                elif indicator == "A" or indicator == "P":
                    if not userchanges:
                        print("You have indicated that you have added or removed a rule, but no changes were initially noted by Mercurial.")
                    address = sections.group(4)
                    if not validurl(address):
                        print("Unrecognised address \"{address}\".".format(address=address))
                    else:
                        # The user has changed the subscription and selected a suitable comment message with a valid address
                        break
                else:
                    print("Unrecognised indicator \"{character}\". Please select either \"A\", \"M\" or \"P\".".format(character=indicator))
                    
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
        
def isglobalelement (domainlist):
    # Check whether all domains are negations
    for domain in domainlist:
        if domain != "" and not domain[0] == "~":
            return False
    return True

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
    if filtertext[0:1] == "@@":
        whitelist = True
        filtertext = filtertext[2:]
    # Remove wildcards from the beginning of the filter
    while True:
        if filtertext[0] != "*":
            break
        else:
            proposed = filtertext[1:]
            if proposed != "" and proposed[0] != "|":
                filtertext = proposed
            else:
                break
    # Remove wildcards from the end of the filter
    while True:
        if filtertext[-1] != "*":
            break
        else:
            proposed = filtertext[:-1]
            if proposed != "" and proposed[-1] != "|":
                # Check for the potential to make regular expressions
                if proposed[0] == "/" and proposed[-1] == "/":
                    break
                else:
                    filtertext = proposed
            else:
                break
    if whitelist:
        filtertext = "@@" + filtertext
    return filtertext
    
if __name__ == '__main__':
    start()
