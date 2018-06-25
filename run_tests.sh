#!/bin/sh
# set variable for seed number to be used
SEED=1
# create a for loop that calls script multiple times
for i in "arrow_ex.png" "bez_ex.png" "heart_ex.png" \
	"lightning_ex.png" "loop_ex.png" "pacman_ex.png" \
	"square_ex.png" "star_ex.png" "tan_ex.png"
do
	python FULL_CPPN_deapea.py i SEED
done	
