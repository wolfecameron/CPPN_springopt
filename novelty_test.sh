#!/bin/sh


# run the script with each image and exit
for i in "heart_ex.png" "pacman_ex.png" "spring10.png" "star_ex.png"
do
	python -m scoop -n 8 FULL_CPPN_noveltyea.py $i 1
done
