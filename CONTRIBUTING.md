## Commit Requirements

After confirming that the rule you want to add works correctly and matches the criteria in the 
[README](README.md), then make sure to do the following:<br>

**Match the rule to the correct folder/file:**<br>
Find the appropriate folder `easylist`, `easylist_cookie`, `easylist_adult`, `easyprivacy`, or `fanboy-addon` and choose the correct file fitting the rule.<br>
For example, an ad that is hidden by the rule `example.com##.ad-12345` would be placed in: `easylist/easylist_specific_hide.txt`<br>

**Order the rule in the file:**<br>
Rules may be categorized using comments: `! <comment>`. If so, place the rule under the correct category. 
Then, insert the rule in the correct position following ASCII ascending sorting. You can use the `fop` script in the root directory to sort by ASCII.

## Commit Policy

EasyList commit messages use three prefixes to indicate the type of a change:
- **A:** *Added* a new filter
- **M:** *Modified* the existing filter for a website, either to match a website's update or to clean up the lists
- **P:** *Problem* fix for a website, such as removing existing filters or making them more specific