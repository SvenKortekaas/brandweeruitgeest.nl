#!/bin/bash

if [ "${APPVEYOR_REPO_BRANCH}" == "master" ]
then

    set -e

    echo "Start uploading"

    pwd

    find . -type f -exec curl -k --ftp-create-dirs -T {} -u ${FTP_USER}:${FTP_PASSWORD} ftp://${FTP_HOST}/{} \;
else
    echo "Not master branch"
fi
exit 0
