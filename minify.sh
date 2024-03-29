#!/bin/bash

set -e

cd public/js/

echo Minify javascript
curl -X POST -s --data-urlencode 'input@hpneo.gmaps.js' https://www.toptal.com/developers/javascript-minifier/api/raw > hpneo.gmaps.min.js
curl -X POST -s --data-urlencode 'input@load-photoswipe.js' https://www.toptal.com/developers/javascript-minifier/api/raw > load-photoswipe.min.js
curl -X POST -s --data-urlencode 'input@gmaps.init.js' https://www.toptal.com/developers/javascript-minifier/api/raw > gmaps.init.min.js
curl -X POST -s --data-urlencode 'input@front.js' https://www.toptal.com/developers/javascript-minifier/api/raw > front.min.js
curl -X POST -s --data-urlencode 'input@leaflet_brw_posten_kennemerland.js' https://www.toptal.com/developers/javascript-minifier/api/raw > leaflet_brw_posten_kennemerland.min.js
echo Replace original with minified JS
rm hpneo.gmaps.js && mv hpneo.gmaps.min.js hpneo.gmaps.js
rm load-photoswipe.js && mv load-photoswipe.min.js load-photoswipe.js
rm gmaps.init.js && mv gmaps.init.min.js gmaps.init.js
rm front.js && mv front.min.js front.js
rm leaflet_brw_posten_kennemerland.js && mv leaflet_brw_posten_kennemerland.min.js leaflet_brw_posten_kennemerland.js

cd ../css/
 
echo Minify css
curl -X POST -s --data-urlencode 'input@animate.css' https://www.toptal.com/developers/cssminifier/api/raw > animate.min.css
curl -X POST -s --data-urlencode 'input@style.red.css' https://www.toptal.com/developers/cssminifier/api/raw > style.red.min.css
curl -X POST -s --data-urlencode 'input@custom.css' https://www.toptal.com/developers/cssminifier/api/raw > custom.min.css
curl -X POST -s --data-urlencode 'input@owl.carousel.css' https://www.toptal.com/developers/cssminifier/api/raw > owl.carousel.min.css
curl -X POST -s --data-urlencode 'input@owl.theme.css' https://www.toptal.com/developers/cssminifier/api/raw > owl.theme.min.css
echo Replace original with minified CSS
rm animate.css && mv animate.min.css animate.css
rm style.red.css && mv style.red.min.css style.red.css
rm custom.css && mv custom.min.css custom.css
rm owl.carousel.css && mv owl.carousel.min.css owl.carousel.css
rm owl.theme.css && mv owl.theme.min.css owl.theme.css

cd ..

echo Minify html files
html-minifier --case-sensitive --collapse-whitespace -o index.min.html index.html
rm index.html && mv index.min.html index.html
html-minifier --case-sensitive --collapse-whitespace -o 2022/index.min.html 2022/index.html
rm 2022/index.html && mv 2022/index.min.html 2022/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2021/index.min.html 2021/index.html
rm 2021/index.html && mv 2021/index.min.html 2021/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2020/index.min.html 2020/index.html
rm 2020/index.html && mv 2020/index.min.html 2020/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2019/index.min.html 2019/index.html
rm 2019/index.html && mv 2019/index.min.html 2019/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2018/index.min.html 2018/index.html
rm 2018/index.html && mv 2018/index.min.html 2018/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2017/index.min.html 2017/index.html
rm 2017/index.html && mv 2017/index.min.html 2017/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2016/index.min.html 2016/index.html
rm 2016/index.html && mv 2016/index.min.html 2016/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2015/index.min.html 2015/index.html
rm 2015/index.html && mv 2015/index.min.html 2015/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2014/index.min.html 2014/index.html
rm 2014/index.html && mv 2014/index.min.html 2014/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2013/index.min.html 2013/index.html
rm 2013/index.html && mv 2013/index.min.html 2013/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2012/index.min.html 2012/index.html
rm 2012/index.html && mv 2012/index.min.html 2012/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2011/index.min.html 2011/index.html
rm 2011/index.html && mv 2011/index.min.html 2011/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2010/index.min.html 2010/index.html
rm 2010/index.html && mv 2010/index.min.html 2010/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2009/index.min.html 2009/index.html
rm 2009/index.html && mv 2009/index.min.html 2009/index.html
html-minifier --case-sensitive --collapse-whitespace -o 2008/index.min.html 2008/index.html
rm 2008/index.html && mv 2008/index.min.html 2008/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2001/index.min.html 12-2001/index.html
rm 12-2001/index.html && mv 12-2001/index.min.html 12-2001/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2002/index.min.html 12-2002/index.html
rm 12-2002/index.html && mv 12-2002/index.min.html 12-2002/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2011/index.min.html 12-2011/index.html
rm 12-2011/index.html && mv 12-2011/index.min.html 12-2011/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2030/index.min.html 12-2030/index.html
rm 12-2030/index.html && mv 12-2030/index.min.html 12-2030/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2031/index.min.html 12-2031/index.html
rm 12-2031/index.html && mv 12-2031/index.min.html 12-2031/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2060/index.min.html 12-2060/index.html
rm 12-2060/index.html && mv 12-2060/index.min.html 12-2060/index.html
html-minifier --case-sensitive --collapse-whitespace -o 12-2061/index.min.html 12-2061/index.html
rm 12-2061/index.html && mv 12-2061/index.min.html 12-2061/index.html
html-minifier --case-sensitive --collapse-whitespace -o betekenis-p2000-meldingen/index.min.html betekenis-p2000-meldingen/index.html
rm betekenis-p2000-meldingen/index.html && mv betekenis-p2000-meldingen/index.min.html betekenis-p2000-meldingen/index.html
html-minifier --case-sensitive --collapse-whitespace -o disclaimer/index.min.html disclaimer/index.html
rm disclaimer/index.html && mv disclaimer/index.min.html disclaimer/index.html
html-minifier --case-sensitive --collapse-whitespace -o voertuigen/index.min.html voertuigen/index.html
rm voertuigen/index.html && mv voertuigen/index.min.html voertuigen/index.html
html-minifier --case-sensitive --collapse-whitespace -o over-ons/index.min.html over-ons/index.html
rm over-ons/index.html && mv over-ons/index.min.html over-ons/index.html
html-minifier --case-sensitive --collapse-whitespace -o posten-kennemerland/index.min.html posten-kennemerland/index.html
rm posten-kennemerland/index.html && mv posten-kennemerland/index.min.html posten-kennemerland/index.html
html-minifier --case-sensitive --collapse-whitespace -o nieuws/index.min.html nieuws/index.html
rm nieuws/index.html && mv nieuws/index.min.html nieuws/index.html

ls -all

exit 0
