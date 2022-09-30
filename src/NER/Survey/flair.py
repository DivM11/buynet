from flair.models import SequenceTagger
from DataLoader import getDF
from flair.data import Sentence

df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


model = SequenceTagger.load("ner-ontonotes-fast")  # .load('ner')


for i in R:

    s = Sentence(i)
    model.predict(s)
    s.to_dict(tag_type="ner")
    print(s)
