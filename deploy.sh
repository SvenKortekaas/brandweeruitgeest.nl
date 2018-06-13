#!/bin/bash

set -e

echo "Start uploading"

pwd

find . -type f -exec curl -k --ftp-create-dirs -T {} -u ${FTP_USER}:${FTP_PASSWORD} ftp://${FTP_HOST}/{} \;

exit 0
