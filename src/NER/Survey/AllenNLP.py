from allennlp.predictors import Predictor
from DataLoader import getDF


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


predictor = Predictor.from_path(
    "https://allennlp.s3.amazonaws.com/models/ner-model-2018.04.26.tar.gz"
)
for i in R:
    results = predictor.predict(sentence=i)
    for word, tag in zip(results["words"], results["tags"]):
        print(f"{word}\t{tag}")
