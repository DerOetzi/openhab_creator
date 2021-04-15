#!/bin/bash

number=$1
shift

echo $@ | /usr/local/bin/signal send $number
