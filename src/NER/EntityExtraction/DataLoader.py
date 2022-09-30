import pandas as pd
import json


def getDF(path):
    i = 0
    f = open(path)
    data = json.load(f)
    df = {}
    for d in data:
        df[i] = d
        i += 1
    return pd.DataFrame.from_dict(df, orient="index")
