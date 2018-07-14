#!/bin/sh
# set variables for all terminal arguments
SEED=1
WEIGHT=30
NODE=3
CON=25
ACT=5
CROSS=10

# create a for loop that calls script multiple times
for i in "lightning_ex.png" "wrench_ex.png" "bez_ex.png" \
		"spring10.png" "pliers_ex.png" "pacman_ex.png"
do
	# run twice to get more chances at each picture
	python -m scoop -n 8 FULL_CPPN_dparamea.py $i $SEED
	python -m scoop -n 8 FULL_CPPN_dparamea.py $i $SEED 
done	
