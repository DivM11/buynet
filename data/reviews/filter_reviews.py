import glob
import json

files = [file for file in glob.glob("*")]
reviews = []
ids = []

ids = []
with open("../ids.txt", "r") as f:
    for line in f:
        ids.append(line.strip())

for filename in files:
    with open(filename, "rb") as f:
        for line in f:
            res_dict = json.loads(line.decode("utf-8"))
            if res_dict["asin"] in ids:
                reviews.append(json.loads(line.strip().decode()))

with open("reviews_electronics_17_18.json", "w") as outfile:
    json.dump(reviews, outfile)
