#!/bin/sh

SEED=1
NGEN=4000

for file in "circle_1.png" "circle_2.png" "circle_3.png" "circle_4.png" \
		"circle_5.png" "circle_6.png" "circle_7.png" "circle_8.png"
do
	python -m scoop -n 8 FULL_CPPN_noveltyea.py $file $SEED $NGEN
done

