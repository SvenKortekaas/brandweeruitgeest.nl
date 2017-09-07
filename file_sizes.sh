#!/bin/bash
find ./public/ \(-iname \*.jpg -o -iname \*.JPG -o -iname \*.jpeg -o -iname \*.JPEG -o -iname \*.png -o -iname \*.PNG -o -iname \*.gif -o -iname \*.GIF\) -type f -size +300k -exec ls -lh {} \; | awk '{ print "Image " $9 " is too big: " $5 }'
exit 0