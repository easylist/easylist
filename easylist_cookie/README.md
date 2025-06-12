Easylist Cookie list covers various cookie, GDPR warnings and notices. 

If there appropiate workaround for a website, we'll let the message show to preserve compatibility. 

## Why Easylist Cookie List?

* uBO Compatible (:style and js snippets)
* Unblocking of blurred content 
* Unblocking of disabled scrollbar & overlays
* Better community support on [Github](https://github.com/easylist/easylist/issues) (open to PR's and Issue Reports)
* Less complex div elements, target divs are more specific and optimised.
* [Updated regularly](https://github.com/easylist/easylist/commits/master/easylist_cookie)

## What is not covered in Easylist Cookie List?

The following nags or warnings that won't be targeted.

* Age checks
* Regional/Country Checks
* Health or Covid warnings
* Tax warning/checks
* Gambling warnings/checks

Note: The only exception if a site combined a cookie consent message with another dialog box then the consent message blocking will take precedence.

## The following sites have no current workaround

| Website | Description | Details |
| --- | --- | --- |
[theverge](https://www.theverge.com/) | Cookie message shows | https://github.com/ryanbr/fanboy-adblock/issues/863 |
[youtube](https://www.youtube.com/) | Consent overlay shows | Hiding overlay will break comments |
[google](https://www.google.com) | Cookie message shows | May affect other parts of google services |
[rainews.it](https://www.rainews.it/tgr/lombardia/notiziari/index.html?/tgr/rainews.html) | Cookie message shows | Needs to accept message to play video |
[Instagram](https://www.instagram.com/) | Consent overlay shows | Breaks loading/posts |
[Medium](https://www.medium.com/) | Cookie message shows | (medium/related medium sites) Consent div id's keep changing, breaks site |
[Facebook](https://www.facebook.com/) | Consent overlay shows | Breaks loading/posts |
[Twitter](https://www.twitter.com/) | Cookie message shows | Consent div id's keep changing, breaks site |
[theguardian](https://theguardian.com/culture/video/2016/apr/25/patrick-stewart-sketch-what-has-the-echr-ever-done-for-us-video) | Consent overlay shows | Breaks comments, and loading of rest of page |
[independent.co.uk](https://www.independent.co.uk/news/world/americas/jeopardy-champ-robbed-amy-schneider-trans-b1987179.html) | Consent overlay shows | Breaks video playback |
[standard](https://www.standard.co.uk/news/uk/brext-passport-rules-uk-woman-hauled-off-flight-tenerife-jet2-b974403.html) | Consent overlay shows | Breaks video playback |
[express.co.uk](https://www.express.co.uk/celebrity-news/1553859/meat-loaf-how-did-he-die-covid-death-cause-age-health-bat-out-of-hell-news-latest-update) | Consent overlay shows | Breaks video playback |
[developer.ing.com](https://developer.ing.com/) | Consent overlay shows | Breaks menus |
[rockpapershotgun.com](https://www.rockpapershotgun.com/final-fantasy-vi-pixel-remaster-is-out-now-finally-giving-us-a-better-version) | Consent overlay shows | Denys access to some site functions |
[dailymotion](https://www.dailymotion.com/) | Consent overlay shows | Denys video playback |
[teacheconomy.de](https://www.teacheconomy.de/) | Consent overlay shows | Stop user clicking on links if not consent message accepted |
[Etsy.com](https://www.etsy.com) | Consent dialogbox shows | Breaks image zooming of products |

## Consent companys
| Consent company | Description | Any way around it? | Details |
| --- | --- | --- | --- |
yahoo consent | popup overlay | Used by some sites like [Engadget](https://engadget.com/) creates a redirect which cannot be blocked. |
trustarc.com/truste.com | popup overlay | No, may depend on the site. Breaks functionality if not accepted | [usa.philips.com](https://www.usa.philips.com/) |
cookiepro.com | popup overlay | No, may depend on the site. Breaks functionality if not accepted | [was removed](https://github.com/easylist/easylist/commit/6714a84e2dde673f5bb70264c61800183ac1dcb5) |
eagerly-tools-cookie | popup icon | Breaks functionality if not accepted | [was removed](https://github.com/easylist/easylist/commit/26a0a76) |

## Removed filters

Some sites will show a cookie consent message while disabling the scroll bar, we can work around this easily. If it's affecting too many sites using the similar template we'll remove the affected generic filters. Future filters specific to each site to avoid breakages. 

Not a complete list, the following filters were removed due to historic issues:

| Filters | What it breaks | 
| --- | --- |
| ###cookie-law-info-bar | Breaks scroll in some implementations |
| ##.wt-cli-cookie-bar-container | Similar to cookie-law-info-bar |
| ###cookieModal | Breaks scroll in some implementations |
| .modal-cacsp-position | Breaks scroll in some implementations |
| ###cookieConsentModal | Breaks scroll in some implementations |
| ##.cookiewall | Breaks scroll when cookiewall used |
| ##div[data-cookie] | Breaks scroll in some implementations |
| ##div[data-nconvert-cookie] | Breaks scroll in some implementations |
| ###orejime/.orejime-Notice | Breaks scroll in some implementations |
| ###consentModal | Breaks scroll in some implementations |
| ##.sqs-announcement-bar | Used for other non-cookie items |
| ##.cc-window[aria-describedby*="consent"] | Breaks scroll in some implementations |
| ##.cc-window[aria-label*="consent"] | Breaks scroll in some implementations |
| ##.cc-grower/##.cc-floating | Breaks scroll in some implementations |
| ###coiOverlay[role="banner"] | Breaks scroll in some implementations |
| ##[data-cookie-id] | Breaks scroll in some implementations |
| ###gdpr-consent/.gdprModal--visible/.gdprModal__placeholder | Breaks scroll in some implementations |
| ##.gdpr-container | Breaks scroll in some implementations |
| ##.gdpr-modal/###gdpr-modal | Breaks scroll in some implementations |
| ###cookiesModal/##.cookiesModal | Breaks scroll in some implementations |
| ##.amgdprcookie-modal-template | Breaks scroll in some implementations |
| ##[aria-label="cookieconsent"] | Breaks scroll in some implementations |

