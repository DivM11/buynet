import pandas as pd
import ijson
import gzip

filename = "meta_Electronics.json.gz"
cols = [
    "description",
    "title",
    "image",
    "brand",
    "rank",
    "main_cat",
    "date",
    "asin",
    "feature",
    "tech1",
    "also_buy",
    "price",
    "also_view",
    "tech2",
    "category",
]
df = pd.DataFrame(columns=cols)

for i in cols:
    with gzip.open(filename, "rb") as f:
        # load json iteratively
        objects = ijson.items(f, i, multiple_values=True)
        columns = list(objects)

    df[i] = columns

df = df.fillna("")
df = df[(df.date.str.contains("2017|2018"))]

df.to_json("./meta_electronics_17_18.json", orient="records")

ids = df["asin"]
del df
ids = list(ids)

with open("../ids.txt", "w") as f:
    for item in ids:
        f.write("%s\n" % item)
