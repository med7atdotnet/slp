#!/bin/bash
find $1 -maxdepth 1 -type f | grep txt | xargs wc -l

