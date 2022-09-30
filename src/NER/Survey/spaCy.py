import spacy
from DataLoader import getDF


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


sp_lg = spacy.load("en_core_web_lg")


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


# somtime it is able to pick up and sometime it is not
for i in R:
    print("sentence", i)
    print([(ent.text.strip(), ent.label_) for ent in sp_lg(i).ents])
