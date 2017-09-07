#!/bin/bash
find ./public/ -name "*.jpg" -type f -size +300k -exec ls -lh {} \; | awk '{ print "jpg/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.JPG" -type f -size +300k -exec ls -lh {} \; | awk '{ print "JPG/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.jpeg" -type f -size +300k -exec ls -lh {} \; | awk '{ print "jpeg/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.JPEG" -type f -size +300k -exec ls -lh {} \; | awk '{ print "JPEG/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.png" -type f -size +300k -exec ls -lh {} \; | awk '{ print "png/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.PNG" -type f -size +300k -exec ls -lh {} \; | awk '{ print "PNG/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.gif" -type f -size +300k -exec ls -lh {} \; | awk '{ print "gif/Image " $9 " is too big: " $5 }' && exit 1
find ./public/ -name "*.GIF" -type f -size +300k -exec ls -lh {} \; | awk '{ print "GIF/Image " $9 " is too big: " $5 }' && exit 1
exit 0
