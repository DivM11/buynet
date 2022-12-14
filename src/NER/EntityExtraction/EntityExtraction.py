import spacy
from DataLoader import getDF
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

prod_pronouns = ["it", "this", "they", "these"]


def apply_extraction(row, nlp, sid):
    review_body = row["reviewText"]
    review_id = row["reviewerID"]
    verified = row["verified"]
    overall = row["overall"]
    product_id = row["asin"]
    summary = row["summary"]
    unixReviewTime = row["unixReviewTime"]
    style = row["style"]
    name = row["reviewerName"]
    vote = row["vote"]
    doc = nlp(review_body)

    # FIRST RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # RULE = M is child of A with a relationshio of amod
    rule1_pairs = []
    for token in doc:
        A = "999999"
        M = "999999"
        if token.dep_ == "amod" and not token.is_stop:
            M = token.text
            A = token.head.text

            # add adverbial modifier of adjective
            # (e.g. 'most comfortable headphones')
            M_children = token.children
            for child_m in M_children:
                if child_m.dep_ == "advmod":
                    M_hash = child_m.text
                    M = M_hash + " " + M
                    break

            # negation in adjective, the "no" keyword is a
            # 'det' of the noun (e.g. no interesting characters)
            A_children = token.head.children
            for child_a in A_children:
                if child_a.dep_ == "det" and child_a.text == "no":
                    neg_prefix = "not"
                    M = neg_prefix + " " + M
                    break

        if A != "999999" and M != "999999":
            x = sid.polarity_scores(token.text)["compound"]
            rule1_pairs.append((A, M, x, 1))

    # SECOND RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # Direct Object - A is a child of something
    # with relationship of nsubj, while
    # M is a child of the same something
    # with relationship of dobj
    # Assumption - A verb will have only one NSUBJ and DOBJ
    add_neg_pfx = False
    rule2_pairs = []
    for token in doc:
        children = token.children
        A = "999999"
        M = "999999"
        add_neg_pfx = False
        for child in children:
            if child.dep_ == "nsubj" and not child.is_stop:
                A = child.text
                # check_spelling(child.text)
            t1 = child.dep_ == "dobj"
            t2 = child.pos_ == "ADJ"
            if (t1 and t2) and not child.is_stop:
                M = child.text
                # check_spelling(child.text)

            if child.dep_ == "neg":
                neg_prefix = child.text
                add_neg_pfx = True

    if add_neg_pfx and M != "999999":
        M = neg_prefix + " " + M

        if A != "999999" and M != "999999":
            rule2_pairs.append((A, M, sid.polarity_scores(M)["compound"], 2))

    # THIRD RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # Adjectival Complement - A is a child
    # of something with relationship of nsubj, while
    # M is a child of the same something
    # with relationship of acomp
    # Assumption - A verb will have only one NSUBJ and DOBJ
    # "The sound of the speakers would be better.
    #  The sound of the speakers could be better"
    # - handled using AUX dependency

    rule3_pairs = []

    for token in doc:

        children = token.children
        A = "999999"
        M = "999999"
        add_neg_pfx = False
        for child in children:
            if child.dep_ == "nsubj" and not child.is_stop:
                A = child.text
                # check_spelling(child.text)

            if child.dep_ == "acomp" and not child.is_stop:
                M = child.text

            # example - 'this could have been better' -> (this, not better)
            if child.dep_ == "aux" and child.tag_ == "MD":
                neg_prefix = "not"
                add_neg_pfx = True

            if child.dep_ == "neg":
                neg_prefix = child.text
                add_neg_pfx = True

        if add_neg_pfx and M != "999999":
            M = neg_prefix + " " + M
            # check_spelling(child.text)

        if A != "999999" and M != "999999":
            rule3_pairs.append((A, M, sid.polarity_scores(M)["compound"], 3))

    # FOURTH RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # Adverbial modifier to a passive verb -
    # A is a child of something with relationship
    # of nsubjpass, while
    # M is a child of the same something
    # with relationship of advmod
    # Assumption - A verb will have only one NSUBJ and DOBJ

    rule4_pairs = []
    for token in doc:

        children = token.children
        A = "999999"
        M = "999999"
        add_neg_pfx = False
        for child in children:
            if (
                child.dep_ == "nsubjpass" or child.dep_ == "nsubj"
            ) and not child.is_stop:
                A = child.text
                # check_spelling(child.text)

            if child.dep_ == "advmod" and not child.is_stop:
                M = child.text
                M_children = child.children
                for child_m in M_children:
                    if child_m.dep_ == "advmod":
                        M_hash = child_m.text
                        M = M_hash + " " + child.text
                        break
                # check_spelling(child.text)

            if child.dep_ == "neg":
                neg_prefix = child.text
                add_neg_pfx = True

        if add_neg_pfx and M != "999999":
            M = neg_prefix + " " + M

        if A != "999999" and M != "999999":
            temp = sid.polarity_scores(M)["compound"]
            rule4_pairs.append((A, M, temp, 4))

    # FIFTH RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # Complement of a copular verb - A is a
    # child of M with relationship of nsubj, while
    # M has a child with relationship of cop
    # Assumption - A verb will have only one NSUBJ and DOBJ

    rule5_pairs = []
    for token in doc:
        children = token.children
        A = "999999"
        buf_var = "999999"
        for child in children:
            if child.dep_ == "nsubj" and not child.is_stop:
                A = child.text
                # check_spelling(child.text)

            if child.dep_ == "cop" and not child.is_stop:
                buf_var = child.text
                # check_spelling(child.text)

        if A != "999999" and buf_var != "999999":
            rule5_pairs.append(
                (A, token.text, sid.polarity_scores(token.text)["compound"], 5)
            )

    # SIXTH RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # Example - "It ok", "ok" is INTJ
    # (interjections like bravo, great etc)

    rule6_pairs = []
    for token in doc:
        children = token.children
        A = "999999"
        M = "999999"
        if token.pos_ == "INTJ" and not token.is_stop:
            for child in children:
                if child.dep_ == "nsubj" and not child.is_stop:
                    A = child.text
                    M = token.text
                    # check_spelling(child.text)

        if A != "999999" and M != "999999":
            rule6_pairs.append((A, M, sid.polarity_scores(M)["compound"], 6))

    # SEVENTH RULE OF DEPENDANCY PARSE -
    # M - Sentiment modifier || A - Aspect
    # ATTR - link between a verb like
    # 'be/seem/appear' and its complement
    # Example: 'this is garbage' -> (this, garbage)

    rule7_pairs = []
    for token in doc:
        children = token.children
        A = "999999"
        M = "999999"
        add_neg_pfx = False
        for child in children:
            if child.dep_ == "nsubj" and not child.is_stop:
                A = child.text
                # check_spelling(child.text)

            if (child.dep_ == "attr") and not child.is_stop:
                M = child.text
                # check_spelling(child.text)

            if child.dep_ == "neg":
                neg_prefix = child.text
                add_neg_pfx = True

        if add_neg_pfx and M != "999999":
            M = neg_prefix + " " + M

        if A != "999999" and M != "999999":
            rule7_pairs.append((A, M, sid.polarity_scores(M)["compound"], 7))

    aspects = []

    aspects = (
        rule1_pairs
        + rule2_pairs
        + rule3_pairs
        + rule4_pairs
        + rule5_pairs
        + rule6_pairs
        + rule7_pairs
    )

    # replace all instances of "it", "this" and "they" with "product"
    aspects = [
        (A, M, P, r) if A not in prod_pronouns else ("product", M, P, r)
        for A, M, P, r in aspects
    ]

    dic = {
        "reviewText": review_body,
        "reviewerID": review_id,
        "verified": verified,
        "overall": overall,
        "asin": product_id,
        "summary": summary,
        "unixReviewTime": unixReviewTime,
        "aspect_pairs": aspects,
        "style": style,
        "reviewerName": name,
        "vote": vote,
    }

    return dic


def init_spacy():
    print("Loading Spacy")
    nlp = spacy.load("en_core_web_lg")
    # for w in stopwords:
    #     nlp.vocab[w].is_stop = True
    # for w in exclude_stopwords:
    #     nlp.vocab[w].is_stop = False
    return nlp


def init_nltk():
    print("\nLoading NLTK....")
    try:
        sid = SentimentIntensityAnalyzer()
    except LookupError:
        print("Installing SentimentAnalyzer")
        nltk.download("vader_lexicon")
        sid = SentimentIntensityAnalyzer()
    print("NLTK successfully loaded")
    return sid


def extract_aspects(reviews, nlp, sid):

    # reviews = df[['review_id', 'review_body']]
    # nlp = init_spacy()
    # sid = init_nltk()

    print("Entering Apply function!")
    aspect_list = reviews.apply(
        lambda row: apply_extraction(row, nlp, sid), axis=1
    )  # going through all the rows in the dataframe

    return aspect_list


def aspect_extraction(nlp, sid):
    root = "/home/ubuntu/buynet/data/reviews"
    df = getDF(path=root + "/reviews_electronics_17_18.json")
    print("=" * 10)
    print(df.columns)
    # df = clean_data(df)
    aspect_list = extract_aspects(df, nlp, sid)

    # print(aspect_list)

    return aspect_list


if __name__ == "__main__":
    nlp = init_spacy()
    sid = init_nltk()
    a = aspect_extraction(nlp, sid)
    a.to_json("Entity.json", orient="split", compression="infer")
