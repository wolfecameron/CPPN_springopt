#!/bin/sh
# set variables for all terminal arguments
SEED=1
WEIGHT=30
NODE=3
CON=25
ACT=5
CROSS=10

# create a for loop that calls script multiple times
for i in "heart_ex.png" "pacman_ex.png" "spring10.png"
do
	# run twice to get more chances at each picture
	python -m scoop -n 8 FULL_CPPN_deapea.py $i $SEED $WEIGHT $NODE $CON $ACT $CROSS
	python -m scoop -n 8 FULL_CPPN_deapea.py $i $SEED $WEIGHT $NODE $CON $ACT $CROSS
done	
