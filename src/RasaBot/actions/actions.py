# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk import word_tokenize
from gensim.models import Doc2Vec
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from elasticsearch import Elasticsearch

# Elastic search Section
es_conn = None


def connect_elastic(ip, port):
    # Connect to an elasticsearch node with the given ip and port
    global es_conn

    es_conn = Elasticsearch([{"host": ip, "port": port}])
    if es_conn.ping():
        print("Connected to elasticsearch...")
    else:
        print("Elasticsearch connection error...")
    return es_conn


def semantic_search(query_vec, es_conn, thresh=1.2, top_n=5):
    # Retrieve top_n semantically similar records for the given query vector
    if not es_conn.indices.exists("electronics"):
        return "No records found"
    s_body = {
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, \
                    'embedding_vectors') + 1.0",
                    "params": {
                        "query_vector": query_vec}}}}}
    # print(query_vec)
    # Semantic vector search with cosine similarity
    result = es_conn.search(index="electronics", body=s_body)
    total_match = len(result["hits"]["hits"])
    # print("Total Matches: ", str(total_match))
    # print(result)
    data = []
    if total_match > 0:
        e_ids = []
        for hit in result["hits"]["hits"]:
            if hit['_score'] > thresh and \
                hit['_source']['asin'] not in e_ids and len(
                    data) <= top_n:
                e_ids.append(hit['_source']['asin'])
                x = {}
                x['description'] = hit['_source']['description']
                x['asin'] = hit['_source']['asin']
                x['brand name'] = hit['_source']['brand']
                data.append(x)
    return data


def default_clean(x):
    if isinstance(x, str):
        x = x.lower()
        x = re.sub('<[^<]+?>', '', x)
        x = re.sub(r'^https?:\/\/.*[\r\n]*', '', x, flags=re.MULTILINE)
        x = re.sub('[^A-Z a-z]+', ' ', x)
        x = " ".join(x.split())
        return x
    else:
        return x


def stop_and_stem(text, stem=True, stemmer=PorterStemmer()):
    '''
    Removes stopwords and does stemming
    '''
    stoplist = stopwords.words('english')
    if stem:
        text_stemmed = [stemmer.stem(word) for word in word_tokenize(
            text) if word not in stoplist]
    else:
        text_stemmed = [word for word in word_tokenize(
            text) if word not in stoplist]
    text = ' '.join(text_stemmed)
    return text


def eval(query_vec, es_conn):

    # sentences = default_clean(sentences)
    # sentences = stop_and_stem(sentences)
    # test_doc = word_tokenize(sentences.lower())
    # query_vec = model.infer_vector(test_doc)
    res = semantic_search(query_vec, es_conn)
    return res


es = connect_elastic("localhost", 9200)
# Returns all the features for a particular product type


class ActionProductSearch(Action):
    def name(self) -> Text:
        return "action_product_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        product = tracker.get_slot("product")
        if product.lower() == "camera":
            fl = ['screen resolution', 'camera resolution', 'battery', 'size']
        elif product.lower() == "television":
            fl = ['size']
        elif product.lower() == "earphone":
            fl = ['sensitivity', 'battery']
        elif product.lower() == "computer":
            fl = ['Hard Drive', 'RAM', 'Display Size', 'Flash Memory Size']
        else:
            fl = ["product not defined"]
        # Use PRODUCT to query in elasticsearch and return the FEATURES
        # available for that product
        feature_list = ''
        for i in fl:
            feature_list += str(i)
            feature_list += '\n'

        # feature_list = '1. screen resolution \n' + '2. size \n' + '3. battery
        # \n' #get from query
        if fl == ["product not defined"]:
            dispatcher.utter_message(feature_list)
        else:
            dispatcher.utter_message(
                'The product that you searched is ' +
                product +
                '. It has the following features \n' +
                feature_list)
        return [SlotSet("product", product)]


class ActionFeatureCompare(Action):
    def name(self) -> Text:
        return "action_feature_comparison"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        featurex = tracker.get_slot("feature")
        return [SlotSet("feature", featurex)]


class ActionFeatureValues(Action):
    def name(self) -> Text:
        return "action_feature_values"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # asin = tracker.get_slot("asin")
        val = tracker.get_slot("feature_value")

        # Query using ASIN for SIMILAR_PRODUCTS and return BRAND and
        # DESCRIPTION of each

        return [SlotSet("feature_value", val)]


class ActionComparisons(Action):
    def name(self) -> Text:
        return "action_comparisons"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # asin = tracker.get_slot("asin")

        # Query using ASIN for SIMILAR_PRODUCTS and return BRAND and
        # DESCRIPTION of each

        operator = tracker.get_slot("comparison")
        feature = tracker.get_slot("feature")
        val = float(tracker.get_slot("feature_value"))
        product = tracker.get_slot("product")
        if product.lower() == "camera":
            res = es.search(
                index="electronics", body={
                    "query": {
                        "match": {
                            "tag_product": "camera"}}})
        elif product.lower() == "television":
            res = es.search(
                index="electronics", body={
                    "query": {
                        "match": {
                            "tag_product": "tv"}}})
        elif product.lower() == "earphone":
            res = es.search(
                index="electronics", body={
                    "query": {
                        "match": {
                            "tag_product": "headphone"}}})
        elif product.lower() == "computer":
            res = es.search(
                index="electronics", body={
                    "query": {
                        "match": {
                            "tag_product": "laptop"}}})
        else:
            dispatcher.utter_message("Product not defined ")
        mem = {"screen resolution": "screen_resolution",
               "resolution": "camera_resolution",
               "sensitivity": "sensitivity",
               "battery": "battery",
               "size": "Size",
               "hard drive": "Hard Drive",
               "ram": "RAM",
               "display size": "Display Size",
               "flash memory size": "Flash Memory Size"
               }
        data = []
        count = 0
        for hit in res['hits']['hits']:
            if count > 3:
                break
            if len(hit["_source"][mem[feature]]) > 0 and len(
                    hit['_source']['image']) > 0:
                temp = float(hit["_source"][mem[feature]][0].split(":")[1])
                if operator.lower() == 'greater than' or operator.lower(
                ) == 'more than':  # g for greater than
                    if temp > val:
                        count += 1
                        x = {}
                        x['url'] = hit['_source']['image']
                        x['description'] = hit["_source"]["description"]
                        x['asin'] = hit["_source"]["asin"]
                        x['brand name'] = hit["_source"]["brand"]
                        data.append(x)
                elif operator.lower() == 'equal to':  # e for equalto
                    if temp == val:
                        count += 1
                        x = {}
                        x['url'] = hit['_source']['image']
                        x['description'] = hit["_source"]["description"]
                        x['asin'] = hit["_source"]["asin"]
                        x['brand name'] = hit["_source"]["brand"]
                        data.append(x)
                elif operator.lower() == 'less than':  # l for less than
                    if temp < val:
                        count += 1
                        x = {}
                        x['url'] = hit['_source']['image']
                        x['description'] = hit["_source"]["description"]
                        x['asin'] = hit["_source"]["asin"]
                        x['brand name'] = hit["_source"]["brand"]
                        data.append(x)
                else:
                    dispatcher.utter_message("Comparison not specified")
            # else:
            #     data.append("Not Found")
        asin = str(data[0]['asin'])  # ['asin']
        dispatcher.utter_message("BRAND NAME: " + str(data[0]['brand name']))
        dispatcher.utter_message("IMAGE OF THE PRODUCT: ")
        Link = str(data[0]['url'][0])
        dispatcher.utter_message(image=Link)
        dispatcher.utter_message(
            "DESCRIPTION OF THE PRODUCT: " +
            default_clean(
                (data[0]['description'][0])))
        return [SlotSet("asin", asin)]
# Returns the specified feature of the current product selected


class ActionFeatureSearch(Action):
    def name(self) -> Text:
        return "action_feature_enquiry"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Query FEATURE for the current product using ASIN to get FEATURE
        # VALUES
        new_feature = tracker.get_slot("feature")
        asin = tracker.get_slot("asin")
        res = es.search(
            index="electronics", body={
                "query": {
                    "match": {
                        "asin": asin}}})
        mem = {"screen resolution": "screen_resolution",
               "resolution": "camera_resolution",
               "sensitivity": "sensitivity",
               "battery": "battery",
               "size": "Size",
               "hard drive": "Hard Drive",
               "ram": "RAM",
               "display size": "Display Size",
               "flash memory size": "Flash Memory Size"
               }
        try:
            new_feature_value = str(
                res['hits']['hits'][0]['_source'][mem[new_feature]][0])
            dispatcher.utter_message(new_feature + ' ' + new_feature_value)
        except BaseException:
            dispatcher.utter_message('Feature not found')
        return []

# Returns reviews of the selected product


class ActionReviewSummary(Action):
    def name(self) -> Text:
        return "action_review_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        asin = tracker.get_slot("asin")
        res = es.search(
            index="electronics", body={
                "query": {
                    "match": {
                        "asin": asin}}})
        ratings = res['hits']['hits'][0]['_source']['overall']
        senti = res['hits']['hits'][0]['_source']['senti_score']
        # reviews = res['hits']['hits'][0]['_source']['top_reviews']

        dispatcher.utter_message(
            "Summary of the Rating distribution of Reviews")
        dispatcher.utter_message(str(ratings))

        if len(senti) != 0:
            dispatcher.utter_message("Attributes and their importance")
            dispatcher.utter_message(str('\n'.join(senti)))
        return []


# Returns reviews of the selected product
class ActionReviewSentiment(Action):
    def name(self) -> Text:
        return "action_review_sentiment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        asin = tracker.get_slot("asin")
        review = tracker.get_slot("review")
        res = es.search(
            index="electronics", body={
                "query": {
                    "match": {
                        "asin": asin}}})
        if review == "positive reviews":
            out = res['hits']['hits'][0]['_source']['pos_rev']
        elif review == "negative reviews":
            out = res['hits']['hits'][0]['_source']['neg_rev']
        elif review == "1 star reviews":
            out = res['hits']['hits'][0]['_source']['one']
        elif review == "2 star reviews":
            out = res['hits']['hits'][0]['_source']['two']
        elif review == "3 star reviews":
            out = res['hits']['hits'][0]['_source']['three']
        elif review == "4 star reviews":
            out = res['hits']['hits'][0]['_source']['four']
        elif review == "5 star reviews":
            out = res['hits']['hits'][0]['_source']['five']
        else:
            out = "error 404"

        dispatcher.utter_message("Reviews Sentiments: " + str(out))
        return []


# Returns a list of similar products (asin id, brand, description)
fname = "E:/IITKGP/Academic_Material/Udemy_PS/PJP2/Sales_Chatbot/\
Amazon_RASA/BotFiles/amz_chatbot/actions/model.doc2vec"
model = Doc2Vec.load(fname)


class ActionSimilarProduct(Action):
    def name(self) -> Text:
        return "action_similar_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # asin = tracker.get_slot("asin")

        # Query using ASIN for SIMILAR_PRODUCTS and return BRAND and
        # DESCRIPTION of each

        asin = tracker.get_slot("asin")
        res = es.search(
            index="electronics", body={
                "query": {
                    "match": {
                        "asin": asin}}})
        re = eval(res['hits']['hits'][0]['_source']['embedding_vectors'], es)
        output = '1. BRAND NAME: ' + str(re[0]['brand name']) + '\n' \
            + '   DESCRIPTION OF THE PRODUCT: ' + \
            str(default_clean(re[0]['description'][0][:300])) +\
            '\n' + '2. BRAND NAME: ' + str(re[1]['brand name']) + '\n' \
            + '   DESCRIPTION OF THE PRODUCT: ' + str(
            default_clean(re[1]['description'][0][:300])) +\
            '\n' + '3. BRAND NAME: ' + str(re[2]['brand name'])\
            + '\n' + '   DESCRIPTION OF THE PRODUCT: ' + \
            str(default_clean(re[2]['description'][0][:300]))

        dispatcher.utter_message(output)

        return []
