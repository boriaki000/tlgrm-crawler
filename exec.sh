#!/usr/bin/sh

while read line
do
  python index.py $line $1
done < ./chat_list.txt