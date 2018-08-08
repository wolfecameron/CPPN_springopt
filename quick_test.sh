#!/bin/sh

SEED_1=2
SEED_2=3
NGEN=5000

for pic in "spring10.png" "pacman_ex.png" "star_ex.png" "hammer_ex.png"
do
	python -m scoop -n 8 FULL_CPPN_noveltyea.py $pic $SEED_1 $NGEN
	python -m scoop -n 8 FULL_CPPN_noveltyea.py $pic $SEED_2 $NGEN
done
