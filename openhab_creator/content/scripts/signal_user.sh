#!/bin/bash

number=$1
shift

if [ "$number" == "-g" ]
then
    number="-g $1"
    shift
fi


echo $@ | /usr/local/bin/signal send $number
