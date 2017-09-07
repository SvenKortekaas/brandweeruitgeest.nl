#!/bin/bash
find ./public/ -type f -size +300k -exec ls -lh {} \; | awk '{ print $8 ": " $5 }'
exit 0