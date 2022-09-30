from sklearn import cluster
from collections import defaultdict

"""## Utils function for Clustering"""

NUM_CLUSTERS = 5


def get_unique_product_ids(reviews_data):
    product_ids = []
    product_ids = [r["asin"] for r in reviews_data]
    return list(set(product_ids))


def get_aspects(reviews_data):
    aspects = []
    for review in reviews_data:
        aspect_pairs = review["aspect_pairs"]
        for noun, _, _, _ in aspect_pairs:
            aspects.append(noun)
    # aspects = [r['aspect_pairs'][0] for r in reviews_data]
    return aspects


def get_aspect_freq_map(aspects):
    aspect_freq_map = defaultdict(int)
    for asp in aspects:
        aspect_freq_map[asp] += 1
    return aspect_freq_map


def get_unique_aspects(aspects):
    unique_aspects = list(set(aspects))  # use this list for clustering
    return unique_aspects


def get_word_vectors(unique_aspects, nlp):
    asp_vectors = []
    for aspect in unique_aspects:
        # print(aspect)
        token = nlp(aspect)
        asp_vectors.append(token.vector)
    return asp_vectors


def get_word_clusters(unique_aspects, nlp):
    print("Found {} unique aspects".format(len(unique_aspects)))
    asp_vectors = get_word_vectors(unique_aspects, nlp)
    # n_clusters = min(NUM_CLUSTERS,len(unique_aspects))
    if len(unique_aspects) <= NUM_CLUSTERS:
        print(
            "Too few aspects ({}) found. No clustering required...".format(
                len(unique_aspects)
            )
        )
        return list(range(len(unique_aspects)))

    print("Running k-means clustering...")
    n_clusters = NUM_CLUSTERS
    kmeans = cluster.KMeans(n_clusters=n_clusters)
    kmeans.fit(asp_vectors)
    labels = kmeans.labels_
    print("Finished running k-means clustering with {}".format(len(labels)))
    return labels


def get_cluster_names_map(asp_to_cluster_map, aspect_freq_map):
    cluster_id_to_name_map = defaultdict()
    # cluster_to_asp_map = defaultdict()
    n_clusters = len(set(asp_to_cluster_map.values()))
    for i in range(n_clusters):
        cluster_asp = [k for k, v in asp_to_cluster_map.items() if v == i]
        ffm = {k: v for k, v in aspect_freq_map.items() if k in cluster_asp}
        ffm = sorted(ffm.items(), key=lambda x: x[1], reverse=True)
        cluster_id_to_name_map[i] = ffm[0][0]

        # cluster_to_asp_map[i] = cluster_nouns

    # print(cluster_to_asp_map)
    return cluster_id_to_name_map
