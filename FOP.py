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
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>."""
# FOP version number
VERSION = 2.996

# Import the key modules
import os, re, subprocess, sys
# Attempt to import a module only available in Python 3 and raise an exception if it is not present
try:
    from urllib.parse import urlparse
except ImportError:
    raise ImportError("The module urllib.parse is unable to be loaded; please upgrade to Python 3.")

# Define some frequently used module functions as local variables for efficiency
parts = re.match
setpattern = re.compile

# Compile some regular expressions to match important filter parts (taken from Wladimir Palant's Adblock Plus source code)
DOMAINPATTERN = setpattern(r"^([^\/\*\|\@\"\!]*?)##")
ELEMENTPATTERN = setpattern(r"^([^\/\*\|\@\"\!]*?)##([^{}]+)$")
OPTIONPATTERN = setpattern(r"^(.*)\$(~?[\w\-]+(?:=[^,\s]+)?(?:,~?[\w\-]+(?:=[^,\s]+)?)*)$")

# Compile regular expressions that match element tags and pseudo classes; "@" indicates either the beginning or the end of a selector
SELECTORPATTERN = setpattern(r"(?<=[\s\[@])([a-zA-Z]*[A-Z][a-zA-Z]*)((?=([\[\]\^\*\$=:@]))|(?=(\s[+>])))")
PSEUDOPATTERN = setpattern(r"(\:[a-zA-Z\-]*[A-Z][a-zA-Z\-]*)(?=([\(\:\@\s]))")
REMOVALPATTERN = setpattern(r"((?<=(@))|(?<=([>+]\s)))([a-zA-Z]+)(?=([#\.]))")

# Compile a regular expression that describes a completely blank line
BLANKPATTERN = setpattern(r"^\s*$")

# Compile a regular expression that validates commit comments
COMMITPATTERN = setpattern(r"^(A|M|P)\:\s(\((.+)\)\s)?(.*)$")

# List the files that should not be sorted, either because they have a special sorting system or because they are not filter files
IGNORE = ("CC-BY-SA.txt", "easytest.txt", "GPL.txt", "MPL.txt")

# List all Adblock Plus options (excepting domain, which is handled separately), as of version 1.3.9.
KNOWNOPTIONS =  ("collapse", "document", "donottrack", "elemhide",
                "image", "object", "object-subrequest", "other",
                "match-case", "script", "stylesheet", "subdocument",
                "third-party", "xbl", "xmlhttprequest")

# List the commands used by different version control systems
GIT = (("git", "diff"), ("git", "commit", "-m"), ("git", "pull"), ("git", "push"))
HG = (("hg", "diff"), ("hg", "commit", "-m"), ("hg", "pull"), ("hg", "push"))
SVN = (("svn", "diff"), ("svn", "commit", "-m"), ("svn", "update"))
REPOTYPES = (("./.git/", GIT), ("./.hg/", HG), ("./.svn/", SVN))

def start ():
    """ Print a greeting message and run FOP in the directories
    specified via the command line, or the current working directory if
    no arguments have been passed."""
    greeting = "FOP (Filter Orderer and Preener) version {version}".format(version = VERSION)
    characters = len(str(greeting))
    print("=" * characters)
    print(greeting)
    print("=" * characters)

    # Convert the directory names to absolute references and visit each unique location
    places = sys.argv[1:]
    if places:
        absplaces = [os.path.normpath(os.path.abspath(place)) for place in places]
        for place in set(absplaces):
            main(place)
            print("")
    else:
        main((os.path.normpath(os.path.abspath(os.getcwd()))))

def main (location):
    """ Find and sort all the files in a given directory, committing
    changes to a repository if one exists"""
    # Change the working directory to the specified directory if it exists, otherwise return
    if os.path.isdir(location):
        os.chdir(location)
    else:
        print("{location} does not exist or is not a folder.".format(location = location))
        return

    # Set the repository type based on hidden directories
    repository = None
    for repotype in REPOTYPES:
        if os.path.isdir(os.path.normpath(repotype[0])):
            repository = repotype[1]
            break
    # If this is a repository, record the initial changes; if this fails, give up trying to use the repository
    if repository:
        try:
            originaldifference = True if subprocess.check_output(repository[0]) else False
        except(subprocess.CalledProcessError, OSError):
            print("The command \"{command}\" was unable to run; FOP will therefore not attempt to use the repository tools. On Windows, this may be an indication that you do not have sufficient privileges to run FOP - the exact reason why is unknown. Please also ensure that your revision control system is installed correctly and understood by FOP.".format(command = repository[0]))
            repository == None
    # Work through the directory and any subdirectories, ignoring hidden directories
    print("\nPrimary location: {folder}{separator}".format(folder = location, separator = os.sep))
    for path, directories, files in os.walk(location):
        print("Current directory: {folder}{separator}".format(folder = os.path.abspath(path), separator = os.sep))
        for direct in directories:
            if direct[0] == ".":
                directories.remove(direct)
        directories = sorted(directories)
        for filename in sorted(files):
            address = os.path.join(path, filename)
            extension = os.path.splitext(filename)[1]
            # Sort all text files that are not blacklisted
            if extension == ".txt" and filename not in IGNORE:
                fopsort(address)
            # Delete unnecessary backups and temporary files
            if extension == ".orig" or extension == ".temp":
                try:
                    os.remove(address)
                except(IOError, OSError):
                    # Ignore errors resulting from deleting an unnecessary file, as they likely indicate that the file has already been deleted
                    pass

    # Offer to commit any changes if in a repository
    if repository:
        commit(repository, location, originaldifference)

def fopsort (filename):
    """ Sort the sections of the file and save the changes, if any have
    been made."""
    changed = False
    temporaryfile = "{filename}.temp".format(filename = filename)
    CHECKLINES = 10
    section = []
    newsectionline = 1
    filterlines = elementlines = 0
    substitute = re.sub

    # Read in the file
    with open(filename, "r", encoding="utf-8", newline="\n") as inputfile, open(temporaryfile, "w", encoding="utf-8", newline="\n") as outputfile:
        for originalline in inputfile:
            line = originalline.strip()
            # Remove blank lines and mark that the file has changed
            if parts(BLANKPATTERN, line):
                changed = True
            else:
                # Ignore comments and, if applicable, sort the preceding section of filters and save them in the new version of the file
                if line[0] == "!" or line[:8] == "%include" or line[0] == "[" and line[-1] == "]":
                    if section:
                        if elementlines > filterlines:
                            outputfile.write("{filters}\n".format(filters = "\n".join(sorted(set(section), key=lambda rule: substitute(DOMAINPATTERN, "", rule)))))
                        else:
                            outputfile.write("{filters}\n".format(filters = "\n".join(sorted(set(section)))))
                        section = []
                        newsectionline = 1
                        filterlines = elementlines = 0
                    if "{line}\n".format(line = line) != originalline:
                        changed = True
                    outputfile.write("{line}\n".format(line = line))
                else:
                    # Neaten up filters and, if necessary, check their type for the sorting algorithm
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
                    # Add the filter to the present section, marking if it is different
                    if "{line}\n".format(line = line) != originalline:
                        changed = True
                    section.append(line)
                    newsectionline += 1
        # At the end of the file, sort and save any remaining filters
        if section:
            if elementlines > filterlines:
                outputfile.write("{filters}\n".format(filters = "\n".join(sorted(set(section), key=lambda rule: substitute(DOMAINPATTERN, "", rule)))))
            else:
                outputfile.write("{filters}\n".format(filters = "\n".join(sorted(set(section)))))

    # Only replace the existing file with the new one if it is different
    if changed:
        # Check the operating system and, if it is Windows, delete the old file to avoid an exception (you are unable to rename files to names already in use)
        if os.name == "nt":
            os.remove(filename)
        os.rename(temporaryfile, filename)
        print("Sorted: {filename}".format(filename = os.path.abspath(filename)))
    else:
        os.remove(temporaryfile)

def filtertidy (filterin):
    """ Sort the options of blocking filters and make the filter text
    lower case if applicable."""
    optionsplit = parts(OPTIONPATTERN, filterin)
    if optionsplit:
        # If applicable, separate and sort the filter options
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
                print("Warning: The option \"{option}\" used on the filter \"{problemfilter}\" is not recognised by FOP".format(option = option, problemfilter = filterin))
            # Check for the match-case option
            if option == "match-case":
                case = True
        # Sort all options other than domain alphabetically
        [optionlist.remove(option) for option in removeentries]
        optionlist = sorted(set(optionlist), key=lambda option: option.strip("~"))
        # If applicable, sort domain restrictions and add them, with the relevant option, to the end of the list of options
        if domainlist:
            optionlist.append("domain={domainlist}".format(domainlist = "|".join(sorted(set(domainlist), key=lambda domain: domain.strip("~")))))

        # If the option "match-case" is not present, make the filter text lower case
        if not case:
            filtertext = filtertext.lower()

        # Return the full filter
        return "{filtertext}${options}".format(filtertext = filtertext, options = ",".join(optionlist))
    else:
        # Remove unnecessary asterisks and return the filter
        return removeunnecessarywildcards(filterin.lower())

def elementtidy (domains, selector):
    """ Sort the domains of element hiding rules, remove unnecessary
    tags and make the relevant sections of the rule lower case."""
    # Order domain names alphabetically, ignoring exceptions
    if "," in domains:
        domains = ",".join(sorted(set(domains.split(",")), key=lambda domain: domain.strip("~")))
    # Mark the beginning and end of the selector with "@"
    selector = "@{selector}@".format(selector = selector)
    each = re.finditer
    # Remove unnecessary tags
    for untag in each(REMOVALPATTERN, selector):
        bc = untag.group(2)
        if bc == None:
            bc = untag.group(3)
        untagname = untag.group(4)
        ac = untag.group(5)
        selector = selector.replace("{before}{untag}{after}".format(before = bc, untag = untagname, after = ac), "{before}{after}".format(before = bc, after = ac), 1)
    # Make the remaining tags lower case wherever possible
    for tag in each(SELECTORPATTERN, selector):
        tagname = tag.group(1)
        ac = tag.group(3)
        if ac == None:
            ac = tag.group(4)
        selector = selector.replace("{tag}{after}".format(tag = tagname, after = ac), "{tag}{after}".format(tag = tagname.lower(), after = ac), 1)
    # Make pseudo classes lower case where possible
    for pseudo in each(PSEUDOPATTERN, selector):
        pseudoclass = pseudo.group(1)
        ac = pseudo.group(3)
        selector = selector.replace("{pclass}{after}".format(pclass = pseudoclass, after = ac), "{pclass}{after}".format(pclass = pseudoclass.lower(), after = ac), 1)
    # Remove the markers from the beginning and end of the selector and return the complete rule
    return "{domain}##{selector}".format(domain = domains, selector = selector[1:-1])

def commit (repotype, location, userchanges):
    """ Commit changes to a repository using the commands provided."""
    difference = subprocess.check_output(repotype[0])
    if not difference:
        print("\nNo changes have been recorded by the repository.")
        return
    print("\nThe following changes have been recorded by the repository:")
    print(difference.decode("utf-8"))
    try:
        # Persistently request for a suitable comment
        while True:
            comment = str(input("Please enter a valid commit comment or quit:\n"))
            if checkcomment(comment, userchanges):
                break
    # Allow users to abort the commit process
    except (KeyboardInterrupt, SystemExit):
        print("\nCommit aborted.")
        return

    print("Comment \"{comment}\" accepted.".format(comment = comment))
    try:
        # Commit the changes
        command = list(repotype[1])
        command.append(comment)
        subprocess.Popen(command).communicate()
        print("\nConnecting to server. Please enter your password if required.")
        # Update the server repository as required by the revision control system
        for command in repotype[2:]:
            subprocess.Popen(command).communicate()
            print("")
    except(subprocess.CalledProcessError):
        print("Unexpected error with the command \"{command}\".".format(command = command))
        raise subprocess.CalledProcessError("Aborting FOP.")
    except(OSError):
        print("Unexpected error with the command \"{command}\".".format(command = command))
        raise OSError("Aborting FOP.")
    print("Completed commit process successfully.")

def isglobalelement (domainlist):
    """ Check whether all domains are negations."""
    for domain in domainlist:
        if domain != "" and not domain[0] == "~":
            return False
    return True

def removeunnecessarywildcards (filtertext):
    """ Where possible, remove unnecessary wildcards from the beginnings
    and ends of blocking filters."""
    whitelist = False
    if filtertext[0:1] == "@@":
        whitelist = True
        filtertext = filtertext[2:]
    while True:
        if filtertext[0] != "*":
            break
        else:
            proposed = filtertext[1:]
            if proposed == "" or proposed[0] == "|":
                break
            else:
                filtertext = proposed
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
        filtertext = "@@{filtertext}".format(filtertext = filtertext)
    return filtertext

def checkcomment(comment, changed):
    """ Check the commit comment and return True if the comment is
    acceptable and False if it is not."""
    sections = parts(COMMITPATTERN, comment)
    if sections == None:
        print("The comment \"{comment}\" is not in the recognised format.".format(comment = comment))
    else:
        indicator = sections.group(1)
        if indicator == "M":
            # Allow modification comments to have practically any format
            return True
        elif indicator == "A" or indicator == "P":
            if not changed:
                print("You have indicated that you have added or removed a rule, but no changes were initially noted by the repository.")
            else:
                address = sections.group(4)
                if not validurl(address):
                    print("Unrecognised address \"{address}\".".format(address = address))
                else:
                    # The user has changed the subscription and has written a suitable comment message with a valid address
                    return True
    print("")
    return False

def validurl (url):
    """ Check that an address has a scheme (e.g. http), a domain name
    (e.g. example.com) and a path (e.g. /), or relates to the internal
    about system."""
    addresspart = urlparse(url)
    if addresspart.scheme and addresspart.netloc and addresspart.path:
        return True
    elif addresspart.scheme == "about":
        return True
    else:
        return False

if __name__ == '__main__':
    start()
