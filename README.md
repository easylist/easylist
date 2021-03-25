# Easylist / Easyprivacy / Fanboy Lists

This Adblock list is maintained by Fanboy, Monzta, Khrin.

**Easylist**

The goal of this repository is block ads, popups and hiding 
 - Scripts (Generic and site-specific)
 - Cosmetic (Generic and domain specific)
 - Ad servers

Issues:

Fix any false-positives that will remove legitimate content (within reason). If it prevent legitimate content from working correctly.
 - Allow direct link fixes
 - Web page rendering issues

**Easyprivacy**

The goal of this repository is block tracking.
 - Analytics
 - Telemetry
 - Pixels
 - Referrers
 - Beacons
 - Fingerprinting
 - Event/perf logging
 - User agent monitoring
 - Cnames
 - Some unnessary third-party scripts
 
When a site is attempting to track, it'll be put into one of 4 categories.
 - Generic blocks (common url/tracking filter patterns) used by 1st/3rd-partys.
 - 1st-party tracking. Self hosted trackers and cnames.
 - Third-party tracking. Hosted by another provider, which hosts a tracking script, but not actually a tracking company.
 - Tracking-servers. Where the server has only one purpose is to tracking/analytics the user, will be blocked the url level.

Issues:

Fix any false-positives that will remove legitimate content (within reason). If it prevent legitimate content from working correctly.
 - Allow direct link fixes
 - Web page rendering issues
