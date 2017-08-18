# easylist

## Overview
Easylist is one of many blacklisting methods to stay safe online.

### Creating filter rules
uBlock Origin has an "element" picker mode; you can use this to select an ad and block it.

Filter syntax can be found with the following links below:
- [Static filter syntax](https://github.com/gorhill/uBlock/wiki/Static-filter-syntax)
- [Cosmetic filters](https://github.com/gorhill/uBlock/wiki/Procedural-cosmetic-filters)
- [Dynamic filters](https://github.com/gorhill/uBlock/wiki/Dynamic-filtering:-rule-syntax)

## Tools
- `genplates.py` is used to generate the lists locally; it requires Jinja2 and Python 3 to be installed. The following files are created: `easylist.txt`, `easyprivacy.txt`, `fanboy-annoyance.txt`, `fanboy-social.txt`
