#!/bin/bash
DIR=`date +%d-%m-%Y-%I-%M-%S-%p`
DEST=/data/db_backups/$DIR/
mkdir $DEST
PGPASSWORD='LKM6U3rD' pg_dump --inserts --column-inserts --username=la_user --host=127.0.0.1 --port=5432 -Fc la > ${DEST}dbbackup.gz
find /data/db_backups/* -type d -mtime +1 -exec rm -rf {} \;
