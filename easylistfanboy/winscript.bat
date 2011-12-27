@echo off
hg pull -u
:: pre-sort
perl docs\sorting\sorter.pl fanboy-adblocklist-current-expanded.txt
perl docs\sorting\sorter.pl fanboy-adblocklist-stats.txt
perl docs\sorting\sorter.pl fanboy-adblocklist-addon.txt
perl docs\sorting\sorter.pl other\adblock-gannett.txt
perl docs\sorting\sorter.pl other\enhancedstats-addon.txt
:: Firefox Regional lists
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-cz.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-esp.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-ind.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-ita.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-jpn.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-krn.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-pol.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-rus-v2.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-swe.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-tky.txt
perl docs\sorting\sorter.pl firefox-regional\fanboy-adblocklist-vtn.txt
:: Opera
perl docs\sorting\sorter.pl opera\urlfilter.ini
perl docs\sorting\sorter.pl opera\urlfilter-cz.ini
perl docs\sorting\sorter.pl opera\urlfilter-esp.ini
perl docs\sorting\sorter.pl opera\urlfilter-ind.ini
perl docs\sorting\sorter.pl opera\urlfilter-jpn.ini
perl docs\sorting\sorter.pl opera\urlfilter-krn.ini
perl docs\sorting\sorter.pl opera\urlfilter-pol.ini
perl docs\sorting\sorter.pl opera\urlfilter-rus.ini
perl docs\sorting\sorter.pl opera\urlfilter-stats.ini
perl docs\sorting\sorter.pl opera\urlfilter-tky.ini
perl docs\sorting\sorter.pl opera\urlfilter-vtn.ini
perl docs\sorting\sorter.pl opera\urlfilter-swe.ini
:: IE Addon List
perl docs\sorting\sorter.pl ie\fanboy-adblock-addon.txt
perl docs\sorting\sorter.pl ie\fanboy-tracking-addon.txt
perl docs\sorting\sorter.pl ie\fanboy-russian-addon.txt
:: Firefox
perl scripts\addChecksum.pl fanboy-adblocklist-current-expanded.txt
perl scripts\addChecksum.pl fanboy-adblocklist-stats.txt
perl scripts\addChecksum.pl fanboy-adblocklist-addon.txt
perl scripts\addChecksum.pl adblock-gannett.txt
perl scripts\addChecksum.pl other\chrome-addon.txt
perl scripts\addChecksum.pl enhancedstats-addon.txt
perl scripts\addChecksum.pl other\tracking-intl.txt
:: Firefox Regional lists
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-chn.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-cz.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-esp.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-ita.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-jpn.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-krn.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-rus-v2.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-swe.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-tky.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-vtn.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-ind.txt
perl scripts\addChecksum.pl firefox-regional\fanboy-adblocklist-pol.txt
:: Opera
perl scripts\addChecksum-opera.pl opera\urlfilter.ini
:: Internet Explorer
perl scripts\addChecksum.pl ie\fanboy-adblock-addon.txt
perl scripts\addChecksum.pl ie\fanboy-tracking-addon.txt
perl scripts\addChecksum.pl ie\fanboy-russian-addon.txt
:: Commit
hg commit -m "%*"
hg push