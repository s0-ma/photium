#!/bin/bash

IMGPATH="/var/samba/Pictures"
python init.py `find $IMGPATH -name "*" -follow | grep -v "\/\."`
