#!/bin/sh
# set variable for seed number to be used
SEED=1
# create a for loop that calls script multiple times
for i in "bez_ex.png" "lightning_ex.png" "loop_ex.png" \
	"pacman_ex.png" "tan_ex.png" "square_ex.png"  
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $i $SEED
done	
