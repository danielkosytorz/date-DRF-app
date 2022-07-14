#!/usr/bin/env bash

until nc -z $DB_HOST $PGPORT
do
 echo Waiting... $DB_HOST
 sleep 1
done

 echo Connected with $POSTGRES_USER