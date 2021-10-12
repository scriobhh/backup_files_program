#!/bin/bash

if [ ! -z $1 ] && [ $1 != "--dry-run" ]
then
    echo -e "\033[0;31mERROR: \033[0m"
    echo -e "ARG \033[1;36m"$1"\033[0m IS INVALID"
    exit -1
fi

python3 backup.py /mnt/e/BACKUPS/ $1
#python3 backup.py /mnt/e/TEST/ $1
