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
VERSION = 2.41

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
OPTIONPATTERN = re.compile(r"^(.*)\$(~?[\w\-]+(?:=[^,\s]+)?(?:,~?[\w\-]+(?:=[^,\s]+)?)*)$")

# The following pattern describes a completely blank line
BLANKPATTERN = re.compile(r"^\s*$")

# The following patterns match element tags and pseudo classes; "@" indicates either the beginning or the end of a selector
SELECTORPATTERN = re.compile(r"((?<=([@\+>\[\)]))|[>+#\.]\s*[\w]+\s+)(\s*[\w]+\s*)(?=([\[@\+>=\]\^\*\$\:]))")
PSEUDOPATTERN = re.compile(r"((?<=[]])|[>+#\.\s]\s*[\w]+)(\s*\:[a-zA-Z\-]{3,}\s*)(?=([\(\:\+\>\@]))")

# The following pattern identifies the sections of commit messages
COMMITPATTERN = re.compile(r"^(\w)\:\s(\((.+)\)\s)?(.*)$")

# The files with the following names should not be sorted, either because they have a special sorting system or because they are not filter files
IGNORE = ("CC-BY-SA.txt", "easytest.txt", "GPL.txt", "MPL.txt")

# The following is a tuple of the Adblock Plus options, as of version 1.3.9
KNOWNOPTIONS =  ("collapse", "document", "donottrack", "elemhide",
                "image", "object", "object-subrequest", "other",
                "match-case", "script", "stylesheet", "subdocument",
                "third-party", "xbl", "xmlhttprequest")

# The following are commands for various version control systems; only the HG commands have been throughly tested
GIT = (("git", "diff"), ("git", "commit", "-m"), ("git", "pull"), ("git", "push"))
HG = (("hg", "diff"), ("hg", "commit", "-m"), ("hg", "pull"), ("hg", "push"))
SVN = (("svn", "diff"), ("svn", "commit", "-m"), ("svn", "update"))
REPOTYPES = (("./.git/", GIT), ("./.hg/", HG), ("./.svn/", SVN))

# Some global regular expression definitions that are used a lot
parts = re.search
substitute = re.sub

def start ():
    # Print the name and version of the program
    print("=" * 44)
    print("FOP (Filter Orderer and Preener) version {version}".format(version=VERSION))
    print("=" * 44)
    
    # Run the program in each of the locations specified in the command line, or the current working directory if no location is specified
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

def main (location):
    # Move to the specified location if it exists
    if os.path.isdir(location):
        os.chdir(location)
    else:
        print("{location} does not exist or is not a folder.".format(location=location))
        return
    
    # Set the repository type based on hidden directories
    repository = None
    for repotype in REPOTYPES:
        if os.path.isdir(repotype[0]):
            repository = repotype[1]
            break
    # Record the initial changes; if this fails, give up trying to use the repository
    if repository:
        try:
            originaldifference = True if subprocess.check_output(repository[0]) else False
        except(subprocess.CalledProcessError, OSError):
            print("The command \"{command}\" was unable to run; FOP will therefore not attempt to use the repository tools. On Windows, this may be an indication that you are required to run FOP as an administrator - the exact reason why is unknown. Please also ensure that your revision control system is installed correctly and understood by FOP.".format(command=repository[0]))
            repository == None
    
    print("\nSorting the contents of {folder}".format(folder=location))
    for path, directory, files in os.walk("."):
        for direct in directory:
            if direct[0] == ".":
                directory.remove(direct)
        for filename in files:
            address = os.path.join(path, filename)
            (name, extension) = os.path.splitext(filename)
            # Sort all text files that are not blacklisted
            if extension == ".txt"  and filename not in IGNORE:
                fopsort(address)
            # Delete unnecessary backups if they are found
            if extension == ".orig":
                os.remove(address)
    
    # Offer to commit any changes if in a repository
    if repository:
        commit(repository, originaldifference)

def fopsort (filename):
    # Read in the file
    with open(filename, "r", encoding="utf-8", newline="\n") as inputfile:
        filecontents = inputfile.read().splitlines()
    if not filecontents:
        return
    if filecontents[-1] == "":
        filecontents = filecontents[:-1]
    
    outfile = []
    CHECKLINES = 10
    section = set()
    newsectionline = 1
    filterlines = elementlines = 0
    # Work through the file line by line
    for line in filecontents:
        if not re.match(BLANKPATTERN, line):
            # Ignore comments and, if applicable, sort the preceding section of filters and add them to the new version of the file
            if line[0] == "!" or line[:8] == "%include" or line[0] == "[" and line[-1] == "]":
                if section:
                    if elementlines > filterlines:
                        outfile.extend(sorted(section, key=lambda rule: substitute(DOMAINPATTERN, "", rule)))
                    else:
                        outfile.extend(sorted(section))
                    section = set()
                    newsectionline = 1
                    filterlines = elementlines = 0
                outfile.append(line)
            else:
                # Neaten up filters, checking their type if necessary
                elementparts = parts(ELEMENTPATTERN, line)
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
            outfile.extend(sorted(section, key=lambda rule: substitute(DOMAINPATTERN, "", rule)))
        else:
            outfile.extend(sorted(section))
    
    # Only save the updated file if it has changed
    if outfile != filecontents:
        with open(filename, "w", encoding="utf-8", newline="\n") as outputfile:
            outputfile.write("\n".join(outfile) + "\n")
        print("{filename} has been sorted".format(filename=filename))
        
def filtertidy (filterin):   
    # If applicable, sort options
    optionsplit = parts(OPTIONPATTERN, filterin)
    if optionsplit:
        # Split, clean and sort options
        filtertext = removeunnecessarywildcards(optionsplit.group(1))
        optionlist = optionsplit.group(2).lower().replace("_", "-").split(",")
        
        domainlist = []
        removeentries = []
        case = False
        for option in optionlist:
            # Detect and separate domain options
            if option[0:7] == "domain=":
                domainlist.extend(option[7:].split("|"))
                removeentries.append(option)
            elif option.strip("~") not in KNOWNOPTIONS:
                print("Warning: The option \"{option}\" used on the filter \"{problemfilter}\" is not recognised by FOP".format(option=option, problemfilter=filterin))
            # Check for the match-case option
            if option == "match-case":
                case = True
        # Complete any required tasks
        [optionlist.remove(option) for option in removeentries]
        # Sort all options other than domain alphabetically
        optionlist = sorted(set(optionlist), key=lambda option: option.strip("~"))
        # If applicable, sort domain restrictions and add the option to the end of the list
        if domainlist:
            optionlist.append("domain=%s" % "|".join(sorted(set(domainlist), key=lambda domain: domain.strip("~"))))
        
        # If the option "match-case" is not present, make the filter text lower case
        if not case:
            filtertext = filtertext.lower()
        
        # Add the options back to the filter and return it
        return "%s$%s" % (filtertext, ",".join(optionlist))
    else:
        # Remove unnecessary asterisks and return the filter
        return removeunnecessarywildcards(filterin.lower())

def elementtidy (domains, selector):
    # Order domain names alphabetically, ignoring exceptions
    domains = ",".join(sorted(set(domains.split(",")), key=lambda domain: domain.strip("~")))
    # Mark the beginning and end of the selector in an unambiguous manner
    selector = "@%s@" % selector
    each = re.finditer
    # Make the tags lower case wherever possible
    for tag in each(SELECTORPATTERN, selector):
        tagname = tag.group(3)
        lowertagname = tagname.lower()
        if tagname != lowertagname:
            bc = tag.group(2)
            if bc == None:
                bc = tag.group(1)
            ac = tag.group(4)
            selector = selector.replace("%s%s%s" % (bc, tagname, ac), "%s%s%s" % (bc, lowertagname, ac), 1)
    # Make pseudo classes lower case where possible
    for pseudo in each(PSEUDOPATTERN, selector):
        pseudoclass = pseudo.group(2)
        lowerpseudoclass = pseudoclass.lower()
        if pseudoclass != lowerpseudoclass:
            ac = pseudo.group(3)
            selector = selector.replace("%s%s" % (pseudoclass, ac), "%s%s" % (lowerpseudoclass, ac), 1)
    # Remove the markers for the beginning and end of the selector, join the rule once more and return it
    return "%s##%s" % (domains, selector[1:-1])

def commit (repotype, userchanges):
    # Only continue if changes have been made to the repository
    difference = subprocess.check_output(repotype[0])
    if not difference:
        print("There are no recorded changes to the repository.")
        return
    print("The following changes have been recorded by the repository:")
    print(difference.decode("utf-8"))
    try:
        # Persistently request for a suitable comment
        while True:
            comment = str(input("Please enter a valid commit comment or quit:\n"))
            if checkcomment(comment, userchanges):
                break
    # Allow users to abort
    except (KeyboardInterrupt, SystemExit):
        print("\nCommit aborted.")
        return
    
    print("Comment \"{comment}\" accepted.".format(comment=comment))
    try:
        # Commit changes
        command = list(repotype[1])
        command.append(comment)
        subprocess.Popen(command).communicate()
        print("\nConnecting to server. Please enter your password if required.")
        # Update the server as required by the revision control system
        for command in repotype[2:]:
            subprocess.Popen(command).communicate()
            print("")
    except(subprocess.CalledProcessError):
        print("Unexpected error with the command \"{command}\".".format(command=command))
        raise subprocess.CalledProcessError("Aborting FOP.")
    except(OSError):   
        print("Unexpected error with the command \"{command}\".".format(command=command))
        raise OSError("Aborting FOP.")

    print("Completed commit process succesfully.")
        
def isglobalelement (domainlist):
    # Check whether all domains are negations
    for domain in domainlist:
        if domain != "" and not domain[0] == "~":
            return False
    return True

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
            if proposed == "" or proposed[0] == "|":
                break
            else:
                filtertext = proposed
    # Remove wildcards from the end of the filter
    while True:
        if filtertext[-1] != "*":
            break
        else:
            proposed = filtertext[:-1]
            if proposed == "" or proposed[-1] == "|" or proposed[0] == "/" and proposed[-1] == "/":
                break
            else:
                filtertext = proposed
    if whitelist:
        filtertext = "@@%s" % filtertext
    return filtertext

def checkcomment(comment, changed):
    sections = parts(COMMITPATTERN, comment)
    if sections == None:
        print("The comment \"{comment}\" is not in the recognised format.".format(comment=comment))
    else:
        indicator = sections.group(1)
        if indicator == "M":
            # Allow modification comments to have practically any format
            return True
        elif indicator == "A" or indicator == "P":
            if not changed:
                print("You have indicated that you have added or removed a rule, but no changes were initially noted by the repository.")
            address = sections.group(4)
            if not validurl(address):
                print("Unrecognised address \"{address}\".".format(address=address))
            else:
                # The user has changed the subscription and selected a suitable comment message with a valid address
                return True
        else:
            print("Unrecognised indicator \"{character}\". Please select either \"A\", \"M\" or \"P\".".format(character=indicator))
    print("")
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

if __name__ == '__main__':
    start()
