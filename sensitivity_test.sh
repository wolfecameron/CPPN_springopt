#!/bin/sh

# set variable for seed number to be used
SEED=1
FILENAME="pacman_ex.png"
WEIGHT=30
NODE=2
CON=10
ACT=5
CROSS=10

# use probabilities multipled by 100 and just divide by 100 in the code
# change weight mutation prob
for i in 15 30 45
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $FILENAME $SEED $i \
			$NODE $CON $ACT $CROSS
done

# node mutation prob
for i in 2 5 8
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $FILENAME $SEED $WEIGHT \
			$i $CON $ACT $CROSS
done


# con mutation prob
for i in 10 20 30
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $FILENAME $SEED $WEIGHT \
			$NODE $i $ACT $CROSS
done

# activation prob
for i in 5 10 20
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $FILENAME $SEED $WEIGHT \
			$NODE $CON $i $CROSS
done

# crossover prob
for i in 10 20 30
do
	python -m scoop -n 8 FULL_CPPN_deapea.py $FILENAME $SEED $WEIGHT \
			$NODE $CON $ACT $i
done