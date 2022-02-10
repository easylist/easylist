# EasyList / EasyPrivacy / Fanboy Lists

These lists are maintained by Fanboy (a.k.a. ryanbr), MonztA, and Khrin.

## EasyList

The goal of this repository is to block ads on English and International sites. First-party ads (that don't link, or passthrough to 3rd-party sites) won't be targeted directly. By blocking the following:
 - Ad scripts (Generic and site-specific)
 - Ad images 
 - Text/CSS ads
 - Pre/mid/end video ads
 - Affiliate links/images/widgets
 - Cosmetic filtering (Generic and site-specific CSS)
 - Ad servers (Block servers that host ads/ad-related contents)
 - Linking, loading or initialising to known Adservers, or ad scripts.
 - Ad servers used as clickthrough servers also blocked outright.
 - Inserting ad elements (cosmetic, servers or scripts) into a page
 - Prevent popups/popunders (Block scripts or domains that cause popups/popunders/ad notifications)
 - Placeholders of non-trivial size (Usually ≥50px tall and ≥50px wide)
 - Invideo/InSlideshow Ads (This is *NOT* the same as a site using embedded youtube videos).
   - 1st or 3rd-party content.
   - Videos/slideshows that aren't directly related to the specific webpage being shown. 
   - May autoplay and/or follows user on scroll. 
 - "Consent messages" using any of these techniques. 

Anti-adblock in Easylist will cover cosmetic and generic blocks checks:
 - Prevent adblock users showing a website
 - Create elements to disrupt viewing a website

For legal reasons, Anti-adblock this will only cover:
 - Adult websites
 - File or Link hosting/sharing
 - Streaming/Torrent/Comic sites
 - Any historical anti-adblock rules

## EasyPrivacy

The goal of this repository is to block tracking and improve end user privacy. By blocking the following:
 - Analytics
 - AntiBot or Bot checks
 - Telemetry
 - Tracking Pixels or cookies (being set, checked or get)
 - Referrers
 - Beacons
 - Fingerprinting
 - Email tracking
 - Impressions / Event / Perf / Pageview logging
 - User agent checks or monitoring
 - Resource miners
 - Hit counters
 - CNAME trackers
 - Notification servers / popups including any tracking covered by Easyprivacy policy
 - Linking, loading or initialising to known tracking servers, or scripts
 - Some unnecessary 3rd-party scripts/images
 - "Consent messages" using any of these tracking techniques, covered by Easyprivacy policy
 
When a site is attempting to track, it'll be put into one of 4 categories.
 - Generic blocks (common URL/tracking filter patterns) used by 1st/3rd-parties.
 - 1st-party tracking. Self-hosted trackers and CNAME trackers.
 - 3rd-party tracking. Hosted by another provider, which hosts a tracking script, but not actually a tracking company.
 - Tracking-servers. Where the server has only one purpose to track/analyze user, will be blocked at the url level.

## Fanboy Lists

This repo also hosts the files for Fanboy's Annoyances List, EasyList Cookie List, Fanboy's Social Blocking List, and Fanboy's Notifications Blocking List.

## List issues

Filter issues can be raised via [E-mail](mailto:easylist@protonmail.com), via [Forum](https://forums.lanik.us/), or via [Github](https://github.com/easylist/easylist/issues). Accountability and responsibility remain with the list authors and not with extensions and/or web browsers. 

Attempt fix website false-positives where applicable such as:
 - Website breakages
 - Allow direct link fixes
 - Web page rendering issues

It is preferable to submit issues instead of pull requests, because the EasyList team will need to look through the sites anyway, and pull requests can fall victim to rebase errors.

## Complaints

If your service is blocked, check the Easylist or Easyprivacy coverage above before submitting any request (and why its blocked).

If your site was added to EasyList or EasyPrivacy:
 - Outline why it shouldn't be added.
 - Filters will not be removed on your word or policy (both can change).
 - The specific commit in question, or specific filter.
 - Is it covered by any of the EasyList/EasyPrivacy requirements?
 
For any issues or questions, create a ticket: [Github](https://github.com/easylist/easylist/issues) [E-mail](mailto:easylist@protonmail.com), or via [Forum](https://forums.lanik.us/).

## Support

EasyList, EasyPrivacy, and Fanboy lists are used in a number of extensions and browsers such as [Adblock Plus](https://adblockplus.org/), [uBlock Origin](https://github.com/gorhill/uBlock), [AdBlock](https://getadblock.com/), [AdGuard](https://adguard.com/), [Brave](https://brave.com/), [Opera](https://www.opera.com/), and [Vivaldi](https://vivaldi.com/).

