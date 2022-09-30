from nltk.tag.stanford import StanfordNERTagger
from DataLoader import getDF


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


print(df.head())


jar = "stanford-ner-2015-04-20/stanford-ner-3.5.2.jar"
model = "stanford-ner-2015-04-20/classifiers/"
st_3class = StanfordNERTagger(
    model + "english.all.3class.distsim.crf.ser.gz", jar, encoding="utf8"
)


for i in R:
    print(st_3class.tag(i.split()))
