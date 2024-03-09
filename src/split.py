import random
import json
from argparse import ArgumentParser
from dataclasses import dataclass
from pprint import pprint

parser = ArgumentParser()

parser.add_argument("--input_file", type=str)
parser.add_argument("--output_file", type=str)
parser.add_argument(
    "--bias", help="If true the output will be biased else it will not be"
)
parser.add_argument(
    "--percentage",
    type=int,
    default=5,
    help="The percentage 5 for 5% , 10 for 10%, correponding to the number of lines kept",
)
parser.add_argument("--threshold_effectif", type=int, help="Minimal number of relation")

args = parser.parse_args()

assert ".json" in args.input_file, "File must be a json"
print("=========== SPLIT ============")
print("File : ", args.input_file)
print("Percetage kept : ", args.percentage, "%")

print(args.bias, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print(type(args.bias))
if args.bias == "false":
    bias = False
else:
    bias = True


@dataclass
class REInputFeatures:
    head_id: str
    tail_id: str
    premise: str
    subj: str
    obj: str
    context: str
    relation: str = None


if args.threshold_effectif is None or bias == True:
    print(" Bias !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # random pickup
    with open(args.input_file, "rt") as f:
        mnli_data = []
        stats = []
        lines = json.load(f)
        print("Number of inputs : ", len(lines))
        print("Number of ouputs : ", round(len(lines) * args.percentage / 100))

        for line in random.choices(lines, k=round(len(lines) * args.percentage / 100)):

            mnli_data.append(
                REInputFeatures(
                    head_id=line["head_id"],
                    tail_id=line["tail_id"],
                    premise=line["premise"],
                    subj=line["subj"],
                    obj=line["obj"],
                    context=line["context"],
                    relation=line["relation"],
                )
            )

        print("Real percentage : ", len(mnli_data) / len(lines))

else:
    # homogeneous random picking throuout all the relations
    with open(args.input_file, "rt") as f:
        mnli_data = []
        stats = []
        lines = json.load(f)
        print("Number of inputs : ", len(lines))
        print("Number of ouputs : ", round(len(lines) * args.percentage / 100))
        relation2data = {}
        for line in lines:
            # accumulate all the elements for each relations
            if line["relation"] in relation2data:
                relation2data[line["relation"]].append(
                    REInputFeatures(
                        head_id=line["head_id"],
                        tail_id=line["tail_id"],
                        premise=line["premise"],
                        subj=line["subj"],
                        obj=line["obj"],
                        context=line["context"],
                        relation=line["relation"],
                    )
                )
            else:
                relation2data[line["relation"]] = [
                    REInputFeatures(
                        head_id=line["head_id"],
                        tail_id=line["tail_id"],
                        premise=line["premise"],
                        subj=line["subj"],
                        obj=line["obj"],
                        context=line["context"],
                        relation=line["relation"],
                    )
                ]
        # compute the effective of each data
        r2eff = {}
        for key, value in relation2data.items():
            num_elements = len(value)
            r2eff[key] = num_elements

        # pich up the relation according to the number of relation
        for rel, effective in r2eff.items():
            if effective == args.threshold_effectif:
                mnli_data.extend(relation2data[rel])  # add all the relation
            if effective > args.threshold_effectif:
                # if more data choose randomnly as much elt as the minimal bound
                mnli_data.extend(
                    random.choices(relation2data[rel], k=args.threshold_effectif)
                )
            # else the class is disgad
        # shuffle the final output
        if args.percentage == 0:
            # 0 means all so just suffle
            random.shuffle(mnli_data)

        else:
            mnli_data = random.choices(
                mnli_data, k=round(len(lines) * args.percentage / 100)
            )
print("dataset size", len(mnli_data))


# save
json.dump(
    [data.__dict__ for data in mnli_data],
    open(args.output_file, "w", encoding="utf-8"),
    indent=4,
)
print("saved at location : ", args.output_file)
