#!/bin/sh
# set variable for seed number to be used
SEED=3

# create a for loop that calls script multiple times
for i in "pacman_ex.png" "heart_ex.png" "star_ex.png" 
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $i $SEED
done	
