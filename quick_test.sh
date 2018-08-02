#!/bin/sh

SEED=3
NGEN=3000

for pic in "spring10.png" "heart_ex.png"
do
	python -m scoop -n 8 FULL_CPPN_noveltyea.py $pic $SEED $NGEN 80 3 5
	python -m scoop -n 8 FULL_CPPN_noveltyea.py $pic $SEED $NGEN 30 3 15
done
