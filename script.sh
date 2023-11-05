#!/bin/bash
BASE=$(pwd)
ROOT=$BASE"/data/WN18RR/"
TRAIN=$ROOT"source/train"
TEST=$ROOT"source/test"
VALID=$ROOT"source/valid"
cd src
# preprocess the raw dataset
python3 data_generator.py --train-path $TRAIN".txt" --valid-path $VALID".txt" --test-path $TEST".txt"

echo "******* TRAIN *******"
# split the train set
#split_values=(5 10 20)
for SPLIT in 5 10 20; do
        # Split train
        echo "$SPLIT"
	!(python3 split.py --input_file $TRAIN".json" --percentage $SPLIT --output_file $ROOT"train_"$SPLIT".json")
	# convert to mnli format
	!(python wn2mnli.py --input_file $ROOT"train_"$SPLIT".json" --output_file $ROOT"train_"$SPLIT".mnli.json")
done
# convert to NLI format
echo "******* TEST *******"
python3 wn2mnli.py --input_file $TEST".json" --output_file $ROOT"test.mnli.json"
echo "******* VALID *******"
python3 wn2mnli.py --input_file $VALID".json" --output_file $ROOT"valid.mnli.json"
