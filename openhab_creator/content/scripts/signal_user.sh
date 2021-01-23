#!/bin/bash

number=$1
shift

if [ "$number" == "BROADCAST" ]; then
    number="-g $1"
    echo "Send Broadcast to $1"
    shift
fi

echo $@ | /usr/local/bin/signal send $number
