@echo off
hg pull -u
:: Firefox
perl addChecksum.pl fanboy-adblocklist-current-expanded.txt
perl addChecksum.pl fanboy-adblocklist-stats.txt  
perl addChecksum.pl fanboy-adblocklist-addon.txt
perl addChecksum.pl adblock-gannett.txt
perl addChecksum.pl other\chrome-addon.txt
perl addChecksum.pl other\enhancedstats-addon.txt
perl addChecksum.pl other\tracking-intl.txt
:: Firefox Regional lists
perl addChecksum.pl firefox-regional\fanboy-adblocklist-chn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-cz.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-esp.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-ita.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-jpn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-krn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-rus-v2.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-swe.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-tky.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-vtn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-ind.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-pol.txt
:: Opera
:: perl addChecksum.pl opera\fanboy-adblocklist-elements-v3.css
perl addChecksum-opera.pl opera\urlfilter.ini
:: Internet Explorer
perl addChecksum.pl ie\fanboy-adblock-addon.txt
perl addChecksum.pl ie\fanboy-tracking-addon.txt
perl addChecksum.pl ie\fanboy-russian-addon.txt
hg commit -m "%*"
hg push