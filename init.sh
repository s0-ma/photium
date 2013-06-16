#!/bin/bash

IMGPATH="/home/tatsuya/Pictures/public"
python init.py `find $IMGPATH -name "*" -follow`
