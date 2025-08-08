#!/usr/bin/env python3
""" Simplified FOP
    Filter Orderer and Preener - Sorting Only
    Based on original FOP by Michael
    
    This simplified version only handles filter sorting without repository management.
"""

# FOP version number
VERSION = 4.0

# Import the key modules
import filecmp, os, re, sys

# Check the version of Python for language compatibility
MAJORREQUIRED = 3
MINORREQUIRED = 1
if sys.version_info < (MAJORREQUIRED, MINORREQUIRED):
    raise RuntimeError("FOP requires Python {reqmajor}.{reqminor} or greater, but Python {ismajor}.{isminor} is being used to run this program.".format(reqmajor = MAJORREQUIRED, reqminor = MINORREQUIRED, ismajor = sys.version_info.major, isminor = sys.version_info.minor))

# Compile regular expressions to match important filter parts
ELEMENTDOMAINPATTERN = re.compile(r"^([^\/\|\@\"\!]*?)#\@?#")
FILTERDOMAINPATTERN = re.compile(r"(?:\$|\,)domain\=([^\,\s]+)$")
ELEMENTPATTERN = re.compile(r"^([^\/\*\|\@\"\!]*?)(#[\@\?]?#)([^{}]+)$")
OPTIONPATTERN = re.compile(r"^(.*)\$(~?[\w\-]+(?:=[^,\s]+)?(?:,~?[\w\-]+(?:=[^,\s]+)?)*)$")

# Compile regular expressions for element tag and selector processing
SELECTORPATTERN = re.compile(r"(?<=[\s\[@])([a-zA-Z]*[A-Z][a-zA-Z0-9]*)((?=([\[\]\^\*\$=:@#\.]))|(?=(\s(?:[+>~]|\*|[a-zA-Z][a-zA-Z0-9]*[\[:@\s#\.]|[#\.][a-zA-Z][a-zA-Z0-9]*))))")
PSEUDOPATTERN = re.compile(r"(\:[a-zA-Z\-]*[A-Z][a-zA-Z\-]*)(?=([\(\:\@\s]))")
REMOVALPATTERN = re.compile(r"((?<=([>+~,]\s))|(?<=(@|\s|,)))(\*)((?=[#\.\[]|\:(?!-abp-contains)))")
ATTRIBUTEVALUEPATTERN = re.compile(r"^([^\'\"\\]|\\.)*(\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\')|\*")
TREESELECTOR = re.compile(r"(\\.|[^\+\>\~\\\ \t])\s*([\+\>\~\ \t])\s*(\D)")
UNICODESELECTOR = re.compile(r"\\[0-9a-fA-F]{1,6}\s[a-zA-Z]*[A-Z]")

# Compile a regular expression that describes a completely blank line
BLANKPATTERN = re.compile(r"^\s*$")

# List the files that should not be sorted
IGNORE = ("CC-BY-SA.txt", "easytest.txt", "GPL.txt", "MPL.txt",
          "easylist_specific_hide_abp.txt", "easyprivacy_specific_uBO.txt", "enhancedstats-addon.txt", "fanboy-tracking", "firefox-regional", "other",
          "easylist_cookie_specific_uBO.txt", "fanboy_annoyance_specific_uBO.txt", "fanboy_newsletter_specific_uBO.txt", "fanboy_notifications_specific_uBO.txt", "fanboy_social_specific_uBO.txt", "fanboy_newsletter_shopping_specific_uBO.txt", "fanboy_agegate_specific_uBO.txt")

# List of domains that should ignore the 8 character size restriction
IGNORE_DOMAINS = {"a.sampl"}

# List all known Adblock Plus options
KNOWNOPTIONS = ("collapse", "csp", "csp=frame-src", "csp=img-src", "csp=media-src", "csp=script-src", "csp=worker-src", "document", "elemhide", "font",
                "genericblock", "generichide", "image", "match-case", "media", "object-subrequest", "object", "other", "ping", "popup", "rewrite=abp-resource:1x1-transparent-gif",
                "rewrite=abp-resource:2x2-transparent-png", "rewrite=abp-resource:32x32-transparent-png", "rewrite=abp-resource:3x2-transparent-png", "rewrite=abp-resource:blank-css",
                "rewrite=abp-resource:blank-html", "rewrite=abp-resource:blank-js", "rewrite=abp-resource:blank-mp3", "rewrite=abp-resource:blank-mp4", "rewrite=abp-resource:blank-text",
                "script", "stylesheet", "subdocument", "third-party", "webrtc", "websocket", "xmlhttprequest")

def start():
    """ Print a greeting message and run FOP in the directories
    specified via the command line, or the current working directory if
    no arguments have been passed."""
    greeting = "Simplified FOP (Filter Orderer and Preener) version {version}".format(version = VERSION)
    characters = len(str(greeting))
    print("=" * characters)
    print(greeting)
    print("=" * characters)

    # Convert the directory names to absolute references and visit each unique location
    places = sys.argv[1:]
    if places:
        places = [os.path.abspath(place) for place in places]
        for place in sorted(set(places)):
            main(place)
            print()
    else:
        main(os.getcwd())

def main(location):
    """ Find and sort all the files in a given directory."""
    # Check that the directory exists, otherwise return
    if not os.path.isdir(location):
        print("{location} does not exist or is not a folder.".format(location = location))
        return

    # Work through the directory and any subdirectories, ignoring hidden directories
    print("\nPrimary location: {folder}".format(folder = os.path.join(os.path.abspath(location), "")))
    for path, directories, files in os.walk(location):
        for direct in directories[:]:
            if direct.startswith(".") or direct in IGNORE:
                directories.remove(direct)
        print("Current directory: {folder}".format(folder = os.path.join(os.path.abspath(path), "")))
        directories.sort()
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
                    # Ignore errors resulting from deleting files
                    pass

def fopsort(filename):
    """ Sort the sections of the file and save any modifications."""
    temporaryfile = "{filename}.temp".format(filename = filename)
    CHECKLINES = 10
    section = []
    lineschecked = 1
    filterlines = elementlines = 0

    # Read in the input and output files concurrently
    with open(filename, "r", encoding = "utf-8", newline = "\n") as inputfile, open(temporaryfile, "w", encoding = "utf-8", newline = "\n") as outputfile:

        # Combines domains for identical rules
        def combinefilters(uncombinedFilters, DOMAINPATTERN, domainseparator):
            combinedFilters = []
            for i in range(len(uncombinedFilters)):
                domains1 = re.search(DOMAINPATTERN, uncombinedFilters[i])
                if i+1 < len(uncombinedFilters) and domains1:
                    domains2 = re.search(DOMAINPATTERN, uncombinedFilters[i+1])
                    domain1str = domains1.group(1)
                
                if not domains1 or i+1 == len(uncombinedFilters) or not domains2 or len(domain1str) == 0 or len(domains2.group(1)) == 0:
                    # last filter or filter didn't match regex or no domains
                    combinedFilters.append(uncombinedFilters[i])
                else:
                    domain2str = domains2.group(1)
                    if domains1.group(0).replace(domain1str, domain2str, 1) != domains2.group(0):
                        # non-identical filters shouldn't be combined
                        combinedFilters.append(uncombinedFilters[i])
                    elif re.sub(DOMAINPATTERN, "", uncombinedFilters[i]) == re.sub(DOMAINPATTERN, "", uncombinedFilters[i+1]):
                        # identical filters. Try to combine them...
                        newDomains = "{d1}{sep}{d2}".format(d1=domain1str, sep=domainseparator, d2=domain2str)
                        newDomains = domainseparator.join(sorted(set(newDomains.split(domainseparator)), key = lambda domain: domain.strip("~")))
                        if (domain1str.count("~") != domain1str.count(domainseparator) + 1) != (domain2str.count("~") != domain2str.count(domainseparator) + 1):
                            # do not combine rules containing included domains with rules containing only excluded domains
                            combinedFilters.append(uncombinedFilters[i])
                        else:
                            # either both contain one or more included domains, or both contain only excluded domains
                            domainssubstitute = domains1.group(0).replace(domain1str, newDomains, 1)
                            uncombinedFilters[i+1] = re.sub(DOMAINPATTERN, domainssubstitute, uncombinedFilters[i])
                    else:
                        # non-identical filters shouldn't be combined
                        combinedFilters.append(uncombinedFilters[i])
            return combinedFilters

        # Writes the filter lines to the file
        def writefilters():
            if elementlines > filterlines:
                uncombinedFilters = sorted(set(section), key = lambda rule: re.sub(ELEMENTDOMAINPATTERN, "", rule))
                outputfile.write("{filters}\n".format(filters = "\n".join(combinefilters(uncombinedFilters, ELEMENTDOMAINPATTERN, ","))))
            else:
                uncombinedFilters = sorted(set(section), key = str.lower)
                outputfile.write("{filters}\n".format(filters = "\n".join(combinefilters(uncombinedFilters, FILTERDOMAINPATTERN, "|"))))

        for line in inputfile:
            line = line.strip()
            if not re.match(BLANKPATTERN, line):
                # Include comments verbatim and sort the preceding section of filters
                if line[0] == "!" or line[:8] == "%include" or line[0] == "[" and line[-1] == "]":
                    if section:
                        writefilters()
                        section = []
                        lineschecked = 1
                        filterlines = elementlines = 0
                    outputfile.write("{line}\n".format(line = line))
                else:
                    # Skip filters containing less than three characters
                    if len(line) < 3:
                        continue
                    # Process filters and check their type for the sorting algorithm
                    elementparts = re.match(ELEMENTPATTERN, line)
                    if elementparts:
                        domains = elementparts.group(1).lower()
                        if lineschecked <= CHECKLINES:
                            elementlines += 1
                            lineschecked += 1
                        line = elementtidy(domains, elementparts.group(2), elementparts.group(3))
                    else:
                        # Skip network domain rules 7 chars or less starting with "|", "||", "|||" etc. or directly with a-z or 0-9 to prevent false positives
                        # unless the domain is in the IGNORE_DOMAINS list
                        if len(line) <= 7 and re.match(r'^\|*[a-zA-Z0-9]', line):
                            # Extract the domain part to check against IGNORE_DOMAINS
                            domain_match = re.match(r'^\|*([^\/\^\$\*]+)', line)
                            if domain_match:
                                domain = domain_match.group(1)
                                if domain not in IGNORE_DOMAINS:
                                    print("Skipped short domain rule: {line} (domain: {domain})".format(line=line, domain=domain))
                                    continue
                        if lineschecked <= CHECKLINES:
                            filterlines += 1
                            lineschecked += 1
                        line = filtertidy(line)
                    # Add the filter to the section
                    section.append(line)
        # At the end of the file, sort and save any remaining filters
        if section:
            writefilters()

    # Replace the existing file with the new one only if alterations have been made
    if not filecmp.cmp(temporaryfile, filename):
        # Check the operating system and delete the old file on Windows
        if os.name == "nt":
            os.remove(filename)
        os.rename(temporaryfile, filename)
        print("Sorted: {filename}".format(filename = os.path.abspath(filename)))
    else:
        os.remove(temporaryfile)

def filtertidy(filterin):
    """ Sort the options of blocking filters and make the filter text
    lower case if applicable."""
    optionsplit = re.match(OPTIONPATTERN, filterin)

    if not optionsplit:
        # Remove unnecessary asterisks from filters without any options
        return removeunnecessarywildcards(filterin)
    else:
        # Separate and sort the filter options in addition to the filter text
        filtertext = removeunnecessarywildcards(optionsplit.group(1))
        optionlist = optionsplit.group(2).lower().replace("_", "-").split(",")

        domainlist = []
        removeentries = []
        for option in optionlist:
            # Detect and separate domain options
            if option[0:7] == "domain=":
                domainlist.extend(option[7:].split("|"))
                removeentries.append(option)
            elif option.strip("~") not in KNOWNOPTIONS:
                print("Warning: The option \"{option}\" used on the filter \"{problemfilter}\" is not recognised".format(option = option, problemfilter = filterin))
        
        # Sort all options other than domain alphabetically
        optionlist = sorted(set(filter(lambda option: option not in removeentries, optionlist)), key = lambda option: (option[1:] + "~") if option[0] == "~" else option)
        
        # If applicable, sort domain restrictions and append them to the list of options
        if domainlist:
            optionlist.append("domain={domainlist}".format(domainlist = "|".join(sorted(set(filter(lambda domain: domain != "", domainlist)), key = lambda domain: domain.strip("~")))))

        # Return the full filter
        return "{filtertext}${options}".format(filtertext = filtertext, options = ",".join(optionlist))

def elementtidy(domains, separator, selector):
    """ Sort the domains of element hiding rules, remove unnecessary
    tags and make the relevant sections of the rule lower case."""
    # Order domain names alphabetically, ignoring exceptions
    if "," in domains:
        domains = ",".join(sorted(set(domains.split(",")), key = lambda domain: domain.strip("~")))
    
    # Mark the beginning and end of the selector with "@"
    selector = "@{selector}@".format(selector = selector)
    each = re.finditer
    
    # Make sure we don't match items in strings
    selectorwithoutstrings = selector
    selectoronlystrings = ""
    while True:
        stringmatch = re.match(ATTRIBUTEVALUEPATTERN, selectorwithoutstrings)
        if stringmatch == None: break
        selectorwithoutstrings = selectorwithoutstrings.replace("{before}{stringpart}".format(before = stringmatch.group(1), stringpart = stringmatch.group(2)), "{before}".format(before = stringmatch.group(1)), 1)
        selectoronlystrings = "{old}{new}".format(old = selectoronlystrings, new = stringmatch.group(2))
    
    # Clean up tree selectors
    for tree in each(TREESELECTOR, selector):
        if tree.group(0) in selectoronlystrings or not tree.group(0) in selectorwithoutstrings: continue
        if tree.group(1) == "(":
            replaceby = "{g2} ".format(g2 = tree.group(2))
        else:
            replaceby = " {g2} ".format(g2 = tree.group(2))
        if replaceby == "   ": replaceby = " "
        selector = selector.replace(tree.group(0), "{g1}{replaceby}{g3}".format(g1 = tree.group(1), replaceby = replaceby, g3 = tree.group(3)), 1)
    
    # Remove unnecessary tags
    for untag in each(REMOVALPATTERN, selector):
        untagname = untag.group(4)
        if untagname in selectoronlystrings or not untagname in selectorwithoutstrings: continue
        bc = untag.group(2)
        if bc == None:
            bc = untag.group(3)
        ac = untag.group(5)
        selector = selector.replace("{before}{untag}{after}".format(before = bc, untag = untagname, after = ac), "{before}{after}".format(before = bc, after = ac), 1)
    
    # Make the remaining tags lower case wherever possible
    for tag in each(SELECTORPATTERN, selector):
        tagname = tag.group(1)
        if tagname in selectoronlystrings or not tagname in selectorwithoutstrings: continue
        if re.search(UNICODESELECTOR, selectorwithoutstrings) != None: break
        ac = tag.group(3)
        if ac == None:
            ac = tag.group(4)
        selector = selector.replace("{tag}{after}".format(tag = tagname, after = ac), "{tag}{after}".format(tag = tagname, after = ac), 1)
    
    # Make pseudo classes lower case where possible
    for pseudo in each(PSEUDOPATTERN, selector):
        pseudoclass = pseudo.group(1)
        if pseudoclass in selectoronlystrings or not pseudoclass in selectorwithoutstrings: continue
        ac = pseudo.group(3)
        selector = selector.replace("{pclass}{after}".format(pclass = pseudoclass, after = ac), "{pclass}{after}".format(pclass = pseudoclass.lower(), after = ac), 1)
    
    # Remove the markers from the beginning and end of the selector and return the complete rule
    return "{domain}{separator}{selector}".format(domain = domains, separator = separator, selector = selector[1:-1])

def removeunnecessarywildcards(filtertext):
    """ Where possible, remove unnecessary wildcards from the beginnings
    and ends of blocking filters."""
    allowlist = False
    hadStar = False
    if filtertext[0:2] == "@@":
        allowlist = True
        filtertext = filtertext[2:]
    while len(filtertext) > 1 and filtertext[0] == "*" and not filtertext[1] == "|" and not filtertext[1] == "!":
        filtertext = filtertext[1:]
        hadStar = True
    while len(filtertext) > 1 and filtertext[-1] == "*" and not filtertext[-2] == "|" and not filtertext[-2] == " ": 
        filtertext = filtertext[:-1]
        hadStar = True
    if hadStar and filtertext[0] == "/" and filtertext[-1] == "/":
        filtertext = "{filtertext}*".format(filtertext = filtertext)
    if filtertext == "*":
        filtertext = ""
    if allowlist:
        filtertext = "@@{filtertext}".format(filtertext = filtertext)
    return filtertext

if __name__ == '__main__':
    start()
