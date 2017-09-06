#!/bin/bash
cd public/js/
curl -X POST -s --data-urlencode 'input@hpneo.gmaps.js' https://javascript-minifier.com/raw > hpneo.gmaps.min.js
curl -X POST -s --data-urlencode 'input@load-photoswipe.js' https://javascript-minifier.com/raw > load-photoswipe.min.js
curl -X POST -s --data-urlencode 'input@gmaps.init.js' https://javascript-minifier.com/raw > gmaps.init.min.js
curl -X POST -s --data-urlencode 'input@front.js' https://javascript-minifier.com/raw > front.min.js
rm hpneo.gmaps.js && mv hpneo.gmaps.min.js hpneo.gmaps.js
rm load-photoswipe.js && mv load-photoswipe.min.js load-photoswipe.js
rm gmaps.init.js && mv gmaps.init.min.js gmaps.init.js
rm front.js && mv front.min.js front.js
cd ../css/
curl -X POST -s --data-urlencode 'input@animate.css' https://cssminifier.com/raw > animate.min.css
curl -X POST -s --data-urlencode 'input@style.red.css' https://cssminifier.com/raw > style.red.min.css
curl -X POST -s --data-urlencode 'input@custom.css' https://cssminifier.com/raw > custom.min.css
curl -X POST -s --data-urlencode 'input@owl.carousel.css' https://cssminifier.com/raw > owl.carousel.min.css
curl -X POST -s --data-urlencode 'input@owl.theme.css' https://cssminifier.com/raw > owl.theme.min.css
rm animate.css && mv animate.min.css animate.css
rm style.red.css && mv style.red.min.css style.red.css
rm custom.css && mv custom.min.css custom.css
rm owl.carousel.css && mv owl.carousel.min.css owl.carousel.css
rm owl.theme.css && mv owl.theme.min.css owl.theme.css
cd ..
find . -type f -exec curl --ftp-create-dirs -T {} -u $FTP_USER:$FTP_PASSWORD ftp://ftp.skortekaas.nl/{} \;
exit 0