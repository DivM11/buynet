from sparknlp.pretrained import PretrainedPipeline
import sparknlp
from DataLoader import getDF


df = getDF("../Data/reviews_Electronics_5.json.gz")
R = df.reviewText.values


# Start Spark Session with Spark NLP
# start() functions has two parameters: gpu and spark23
# sparknlp.start(gpu=True) will start the session with GPU support
# sparknlp.start(sparrk23=True) is when you have Apache Spark 2.3.x installed
spark = sparknlp.start(gpu=True)

pipeline = PretrainedPipeline("recognize_entities_dl", "en")
result = pipeline.annotate(
    "The Mona Lisa is a 16th century oil painting created by Leonardo"
)
