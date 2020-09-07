#!/bin/bash

workdir=$1

for test_file in $workdir/tests/*
do
    if ! python3 $workdir/main.py < $test_file
    then
        exit 1
    fi
done
