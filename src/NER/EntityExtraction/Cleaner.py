import pandas as pd


def clean_data(df):

    pd.options.mode.chained_assignment = None

    print("******Cleaning Started*****")

    print(f"Shape of df before cleaning : {df.shape}")
    df[""] = pd.to_datetime(df["reviewTime"])
    df = df[df["reviewText"].notna()]
    df["reviewText"] = df["reviewText"].str.replace("<br />", " ")
    df["reviewText"] = df["reviewText"].str.replace("\[?\[.+?\]?\]", " ")
    df["reviewText"] = df["reviewText"].str.replace("\/{3,}", " ")
    df["reviewText"] = df["reviewText"].str.replace("\&\#.+\&\#\d+?;", " ")
    df["reviewText"] = df["reviewText"].str.replace("\d+\&\#\d+?;", " ")
    df["reviewText"] = df["reviewText"].str.replace("\&\#\d+?;", " ")

    # facial expressions
    df["reviewText"] = df["reviewText"].str.replace("\:\|", "")
    df["reviewText"] = df["reviewText"].str.replace("\:\)", "")
    df["reviewText"] = df["reviewText"].str.replace("\:\(", "")
    df["reviewText"] = df["reviewText"].str.replace("\:\/", "")
    df["reviewText"] = df["reviewText"].str.replace("\...", "")
        
    # replace multiple spaces with single space
    df["reviewText"] = df["reviewText"].str.replace("\s{2,}", " ")

    df["reviewText"] = df["reviewText"].str.lower()
    print(f"Shape of df after cleaning : {df.shape}")
    print("******Cleaning Ended*****")

    return df
