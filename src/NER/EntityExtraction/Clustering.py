import json
import spacy

from utils import (
    get_aspects,
    get_aspect_freq_map,
    get_word_clusters,
    get_cluster_names_map,
    get_unique_product_ids,
)
import numpy as np

f = open("Entity.json")
NUM_CLUSTERS = 5
reviews_data = json.load(f)["data"]

"""## Clustering"""


def add_clusters_to_reviews(reviews_data, nlp):
    product_aspects = get_aspects(reviews_data)
    print("Total aspects found: {}".format(len(product_aspects)))
    aspect_freq_map = get_aspect_freq_map(product_aspects)
    unique_aspects = aspect_freq_map.keys()
    print("Runnig clustering on {} unique aspects".format(len(unique_aspects)))

    aspect_labels = get_word_clusters(unique_aspects, nlp)
    asp_to_cluster_map = dict(zip(unique_aspects, aspect_labels))
    cnm = get_cluster_names_map(asp_to_cluster_map, aspect_freq_map)
    updated_reviews = []

    m = {}
    summ = {"product_id": reviews_data[0]["asin"]}
    for review in reviews_data:
        result = []
        aspect_pairs = review["aspect_pairs"]
        for noun, adj, polarity, rule in aspect_pairs:
            cluster_label_id = asp_to_cluster_map[noun]
            cluster_label_name = cnm[cluster_label_id]
            if noun in m:
                m[cluster_label_name].append(polarity)
            else:
                m[cluster_label_name] = [polarity]
            result.append(
                {
                    "noun": noun,
                    "adj": adj,
                    "rule": rule,
                    "polarity": polarity,
                    "cluster": cluster_label_name,
                }
            )

        assert len(result) == len(aspect_pairs)

        updated_reviews.append(
            {
                "review_id": review["reviewerID"],
                "product_id": review["asin"],
                "aspect_pairs": result,
            }
        )
    for key in m:
        summ[key] = np.array(m[key]).mean()
    return updated_reviews, [summ]


def update_reviews_data(reviews_data, nlp):
    updated_reviews = []
    summ_reviews = []
    product_ids = get_unique_product_ids(reviews_data)
    print("Total number of unique products: {}".format(len(product_ids)))

    nar = [r for r in reviews_data if len(r["aspect_pairs"]) == 0]
    print("Total reviews found with no aspect pairs: {}".format(len(nar)))

    for prod_id in product_ids:
        print("\nRunning clustering for product ID - {}".format(prod_id))
        product_reviews = [r for r in reviews_data if r["asin"] == prod_id]

        product_upd_reviews, s = add_clusters_to_reviews(product_reviews, nlp)
        updated_reviews.extend(product_upd_reviews)
        summ_reviews.extend(s)
    print("\n----------------***----------------")
    print("Updating final results")
    with open("results_file.json", "a") as f:
        json.dump(updated_reviews, f)
    with open("summ_file.json", "a") as f:
        json.dump(summ_reviews, f)

    print("Finished writing results to json!!")
    print("----------------***----------------")


"""## Calling Clustering Function"""
nlp = spacy.load("en_core_web_lg")
print("Running clustering...")
update_reviews_data(reviews_data, nlp)
