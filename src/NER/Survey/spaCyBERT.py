import spacy
import torch
from DataLoader import getDF


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


is_using_gpu = spacy.prefer_gpu()
if is_using_gpu:
    torch.set_default_tensor_type("torch.cuda.FloatTensor")

nlp = spacy.load("en_trf_bertbaseuncased_lg")
