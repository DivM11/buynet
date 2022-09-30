from bs4 import BeautifulSoup
from nltk.stem.lancaster import LancasterStemmer
import re
from nltk.stem import WordNetLemmatizer
from contractions import contractions_dict
import unicodedata
from nltk.corpus import stopwords
import pandas as pd
import json
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def getDF(path):
    i = 0
    f = open(path)
    data = json.load(f)
    df = {}
    for d in data:
        df[i] = d
        i += 1
    return pd.DataFrame.from_dict(df, orient="index")


def clean_data(review_json, metadata_json):
    # Import reviews data
    review_df = getDF(review_json)
    # change column name
    review_df = review_df.rename(columns={'overall': 'Rating'})

    print("Total data:", str(review_df.shape))

    # Import reviews data
    meta_df = getDF(metadata_json)

    print("Total data:", str(meta_df.shape))

    # MERGING PRODUCT REVIEW AND METADATA IN PANDAS
    df_prod1 = pd.merge(review_df, meta_df, on='asin', how='left')

    # DROP NULL VALUES IN REVIEWTEXT COLUMN IN PANDAS
    df_prod2 = df_prod1.dropna(subset=['reviewText'])

    # CONCATENATE REVIEWTEXT AND SUMMARY
    df_prod2['review_text'] = df_prod2[['summary', 'reviewText']].apply(
        lambda x: " ".join(str(y) for y in x if str(y) != 'nan'), axis=1)
    df_prod2 = df_prod2.drop(['reviewText', 'summary'], axis=1)

    # After removing duplicates
    df_prod2 = df_prod2.drop_duplicates(
        ['asin', 'reviewerName', 'unixReviewTime'], keep='first')

    # Convert time object to datetime and create a new column named 'time'
    df_prod2['time'] = df_prod2.reviewTime.str.replace(',', "")
    df_prod2['time'] = pd.to_datetime(df_prod2['time'], format='%m %d %Y')
    # Drop redundant 'reviewTime' column
    df_prod2 = df_prod2.drop('reviewTime', axis=1)

    # Classify ratings as good
    good_rate = len(df_prod2[df_prod2['Rating'] >= 3])
    bad_rate = len(df_prod2[df_prod2['Rating'] < 3])

    # Printing rates and their total numbers
    print('Good ratings : {} reviews for products'.format(good_rate))
    print('Bad ratings : {} reviews for products'.format(bad_rate))

    # Add new rating class column
    df_prod2['rating_class'] = df_prod2['Rating'].apply(
        lambda x: 'bad' if x < 3 else'good')

    # ## Text Preprocessing

    # calculate raw tokens in order to measure of cleaned tokens

    from nltk.tokenize import word_tokenize
    raw_tokens = len(
        [w for t in (df_prod2["review_text"].apply(word_tokenize))for w in t])
    print('Number of raw tokens: {}'.format(raw_tokens))

    # Lemmatization

    def strip_html(text):
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()

    def remove_between_square_brackets(text):
        return re.sub(r'\[[^]]*\]', '', text)

    def denoise_text(text):
        text = strip_html(text)
        text = remove_between_square_brackets(text)
        return text

    # Define function to expand contractions

    def expand_contractions(text):
        contractions_pattern = re.compile(
            '({})'.format(
                '|'.join(
                    contractions_dict.keys())),
            flags=re.IGNORECASE | re.DOTALL)

        def expand_match(contraction):
            match = contraction.group(0)
            if contractions_dict.get(match):
                expanded_contraction = contractions_dict.get(match)
            else:
                expanded_contraction = contractions_dict.get(match.lower())
            return expanded_contraction

        expanded_text = contractions_pattern.sub(expand_match, text)
        expanded_text = re.sub("'", "", expanded_text)
        return expanded_text

    # special_characters removal

    def remove_special_characters(text, remove_digits=True):
        pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
        text = re.sub(pattern, '', text)
        return text

    def remove_non_ascii(words):
        """Remove non-ASCII characters from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = unicodedata.normalize(
                'NFKD',
                word).encode(
                'ascii',
                'ignore').decode(
                'utf-8',
                'ignore')
            new_words.append(new_word)
        return new_words

    def to_lowercase(words):
        """Convert all characters to lowercase from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = word.lower()
            new_words.append(new_word)
        return new_words

    def remove_punctuation_and_splchars(words):
        """Remove punctuation from list of tokenized words"""
        new_words = []
        for word in words:
            new_word = re.sub(r'[^\w\s]', '', word)
            if new_word != '':
                new_word = remove_special_characters(new_word, True)
                new_words.append(new_word)
        return new_words

    stopword_list = stopwords.words('english')
    stopword_list.remove('no')
    stopword_list.remove('not')

    def remove_stopwords(words):
        """Remove stop words from list of tokenized words"""
        new_words = []
        for word in words:
            if word not in stopword_list:
                new_words.append(word)
        return new_words

    def stem_words(words):
        """Stem words in list of tokenized words"""
        stemmer = LancasterStemmer()
        stems = []
        for word in words:
            stem = stemmer.stem(word)
            stems.append(stem)
        return stems

    def lemmatize_verbs(words):
        """Lemmatize verbs in list of tokenized words"""
        lemmatizer = WordNetLemmatizer()
        lemmas = []
        for word in words:
            lemma = lemmatizer.lemmatize(word, pos='v')
            lemmas.append(lemma)
        return lemmas

    def normalize(words):
        words = remove_non_ascii(words)
        words = to_lowercase(words)
        words = remove_punctuation_and_splchars(words)
        words = remove_stopwords(words)
        return words

    def lemmatize(words):
        lemmas = lemmatize_verbs(words)
        return lemmas

    # In[30]:

    def normalize_and_lemmaize(input):
        sample = denoise_text(input)
        sample = expand_contractions(sample)
        sample = remove_special_characters(sample)
        words = nltk.word_tokenize(sample)
        words = normalize(words)
        lemmas = lemmatize(words)
        return ' '.join(lemmas)

    df_prod2['clean_text'] = df_prod2['review_text'].map(
        lambda text: normalize_and_lemmaize(text))

    # Cleaning the Text

    # Let's put aside number of raw tokens in order to measure of cleaned
    # tokens
    clean_tokens = len(
        [w for t in (df_prod2["clean_text"].apply(word_tokenize)) for w in t])
    print('Number of clean tokens: {}\n'.format(clean_tokens))
    print('Percentage of removed tokens: {0:.2f}'.format(
        1 - (clean_tokens / raw_tokens)))

    # df_prod2.to_csv('clean_reviews.csv', sep=',',
    # encoding='utf-8', index = False)

    df = df_prod2
    # Create a "year" column and drop time column
    df['unixReviewTime'] = pd.to_datetime(df['unixReviewTime'])
    df['year'] = df['unixReviewTime'].dt.year
    df = df.drop('unixReviewTime', axis=1)

    df = df.dropna(subset=['clean_text'])

    # Function for creating a column token
    def token(text):
        token = [w for w in nltk.word_tokenize(text)]
        return token

    # To create token feature
    df['token'] = df['clean_text'].apply(token)

    # Function for creating a column to see the length of the review text
    def length(text):
        length = len([w for w in nltk.word_tokenize(text)])
        return length

    # Apply length function to create review length feature
    df['review_length'] = df['review_text'].apply(length)

    # Removed reviews with more than 150 words

    df3 = df.drop(df[(df['review_length'] > 200)].index)

    df3['rating_class_num'] = df3['rating_class'].map({'good': 1, 'bad': 0})

    # df3.to_csv('Reduced_Cleaned_Reviews_electronics.csv',
    # sep=',', encoding='utf-8', index = False)

    # clean_file = df3.to_json('Reduced_Cleaned_Reviews_electronics.json')
    clean_file = df3.to_csv('Reduced_Cleaned_Reviews_electronics.csv')

    return clean_file
