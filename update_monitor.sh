#!/bin/bash
NOTIFYPATH=/var/samba/Pictures
TIMEOUT=20
WAS_UPDATED=0
IS_UPDATED=0
/usr/bin/inotifywait -e create,delete,modify,moved_to -mrq $NOTIFYPATH | while [ 1 ]; do
	IS_UPDATED=0
	while read -t $TIMEOUT line; do
		IS_UPDATED=1
		WAS_UPDATED=1
	done

	if [ $IS_UPDATED -eq 0 ]; then
		if [ $WAS_UPDATED -eq 1 ];then
			./init.sh
			echo "updated"
			WAS_UPDATED=0
		fi
	fi
done
