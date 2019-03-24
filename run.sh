#!/bin/bash

if [ -f output.txt ]
then
    if [ -s output.txt ]
    then
        rm -f output.txt
        python index.py >> output.txt
        python test.py
    else
        rm -f output.txt
        python index.py >> output.txt
        python test.py
    fi
else
    python index.py >> output.txt
    python test.py
fi
