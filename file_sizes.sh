#!/bin/bash
find ./public/ -name "*.jpg" -type f -size +300k -exec ls -lh {} \; | awk '{ print "jpg/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.JPG" -type f -size +300k -exec ls -lh {} \; | awk '{ print "JPG/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.jpeg" -type f -size +300k -exec ls -lh {} \; | awk '{ print "jpeg/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.JPEG" -type f -size +300k -exec ls -lh {} \; | awk '{ print "JPEG/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.png" -type f -size +300k -exec ls -lh {} \; | awk '{ print "png/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.PNG" -type f -size +300k -exec ls -lh {} \; | awk '{ print "PNG/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.gif" -type f -size +300k -exec ls -lh {} \; | awk '{ print "gif/Image " $9 " is too big: " $5 }'
find ./public/ -name "*.GIF" -type f -size +300k -exec ls -lh {} \; | awk '{ print "GIF/Image " $9 " is too big: " $5 }'

# Find a way to do this in one line.....
if [ -n "$(find ./public/ -name "*.jpg" -type f -size +300)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.JPG" -type f -size +300k)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.jpeg" -type f -size +300k)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.JPEG" -type f -size +300k)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.png" -type f -size +300k)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.PNG" -type f -size +300k)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.gif" -type f -size +300k)" ]
then
  exit 1
elif [ -n "$(find ./public/ -name "*.GIF" -type f -size +300k)" ]
then
  exit 1
else
  echo "No problems. All images are less than 300kb"
fi

exit 0
