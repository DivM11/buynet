# Load pre-existing spacy model and importing requirements
import spacy
import pickle
import random
from spacy.util import minibatch, compounding

nlp = spacy.load("en_core_web_sm")
# Getting the pipeline component
ner = nlp.get_pipe("ner")

with open("ner_train.txt", "rb") as fp:  # Unpickling
    TRAIN_DATA = pickle.load(fp)

# Adding labels to the `ner`

for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable pipeline components you dont need to change
pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

# TRAINING THE MODEL
with nlp.disable_pipes(*unaffected_pipes):

    # Training for 30 iterations
    for iteration in range(30):

        # shuufling examples  before every iteration
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(
                texts,  # batch of texts
                annotations,  # batch of annotations
                drop=0.5,  # dropout - make it harder to memorise data
                losses=losses,
            )
            print("Losses", losses)
