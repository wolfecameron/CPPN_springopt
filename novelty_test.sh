#!/bin/sh

TOTAL_IT=5

# run the script total it number of times and exit
for i in 1 2 3 4 5
do
	python -m scoop -n 8 FULL_CPPN_noveltyea.py 1
done
