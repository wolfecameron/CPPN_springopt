#!/bin/sh
# set variable for seed number to be used
SEED=3
# create a for loop that calls script multiple times
for i in "bez_ex.png" "bez_ex" "loop_ex.png" "pacman_ex.png" 
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $i $SEED
done	
