@echo off
hg update
hg pull --rebase remote
hg pull
:: Firefox
perl addChecksum.pl fanboy-adblocklist-adult.txt
perl addChecksum.pl fanboy-adblocklist-current-expanded.txt
perl addChecksum.pl fanboy-adblocklist-stats.txt  
perl addChecksum.pl fanboy-adblocklist-dimensions-v2.txt
perl addChecksum.pl fanboy-adblocklist-current-p2p.txt
perl addChecksum.pl adblock-gannett.txt
perl addChecksum.pl fanboy-adblocklist-cz.txt
:: RUS
perl addChecksum.pl fanboy-morpeh-rus.txt
:: Firefox Regional lists
perl addChecksum.pl firefox-regional\fanboy-adblocklist-chn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-cz.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-esp.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-jpn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-krn.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-rus.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-rus-v2.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-swe.txt
perl addChecksum.pl firefox-regional\fanboy-adblocklist-tky.txt
:: Opera
:: test
perl addChecksum.pl opera\fanboy-adblocklist-elements-v3.css
perl addChecksum-opera.pl opera\urlfilter.ini
perl addChecksum-opera.pl opera\urlfilter-chn.ini
perl addChecksum-opera.pl opera\urlfilter-cz.ini
perl addChecksum-opera.pl opera\urlfilter-esp.ini
perl addChecksum-opera.pl opera\urlfilter-jpn.ini
perl addChecksum-opera.pl opera\urlfilter-krn.ini
perl addChecksum-opera.pl opera\urlfilter-stats.ini
perl addChecksum-opera.pl opera\urlfilter-tky.ini
:: Iron
perl addChecksum-opera.pl iron/adblock-beta.ini
perl addChecksum-opera.pl iron/adblock-chn.ini
perl addChecksum-opera.pl iron/adblock-cz.ini
perl addChecksum-opera.pl iron/adblock-esp.ini
perl addChecksum-opera.pl iron/adblock-jpn.ini
perl addChecksum-opera.pl iron/adblock-krn.ini
perl addChecksum-opera.pl iron/adblock-stats.ini
perl addChecksum-opera.pl iron/adblock-trk.ini
:: Now sync
hg add .
hg commit -m "%*"
hg push
