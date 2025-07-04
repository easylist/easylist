## What

Trying to ensure the best user experience and limit any webcompat issues. Just because we can hide a cookie messgae with a CSS element, doesn't mean it should be the best solution. We have many tools to counter these GDPR/CPPA Cookie consents, as list authors we need to check which option is the best.

* Generic cosmetics (generally avoided to avoid more widespread false positives)
* Specific cosmetics  (better
* set-cookie, set-local-storage-item
* trusted-set- (for more complex additions) 

## To ensure Cookies messages are removed correctly and to avoid issues like;

* Broken scrolls
* Overlays
* Mouse clicks not working
* Allow embedded social media and embedded video to work
* And double/triple checking implemented rules work.

How should a cookie consent be addressed? 

## For a specific cosmetic element addition:

* If the scroll bar is not disabled
* No overlays
* The cookie consent popup is just a simple element, unlikely being checked by a website.
* If the site functions normally with the cookie consent shown in the foreground.
* When implemented go through the Checklist to ensure no breakage.

## When a more advances set-* or trusted-set-* should be used

- If the cosmetics requires permission to access the site
- If there is extensive "Customise" or "Options".
- Or no option to disagree, and only Agree.
- Using a consent manager service
- Embedded options like social/youtube would still be shown

## Checklist when implementing cookie consent fixes:

- Check 2-3 pages to ensure rule doesn't cause issues, anything usable.
- Check scroll and mouse click works.
- When adding a "new" consent script, check that current rules/and previously (via git log/blame).
- Check embedded items like social media and videos work.
- Check other adblock extensions [like uBO](https://github.com/uBlockOrigin/uAssets/blob/master/filters/annoyances-cookies.txt) and/or Brave to ensure the site isn't already fixed.
- Banks, Financial, Travel websites should mostly/always be used using set- or trusted-set- rules, given the importance.
- TLDR: If there is a chance that we're not sure of website breakage, move to a set- or trusted-set- rule.


