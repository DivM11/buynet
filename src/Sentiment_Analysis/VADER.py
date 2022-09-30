import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, f1_score
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')


def plot_cm(y_test, y_pred, target_names=['bad', 'good'],
            figsize=(5, 3)):
    """Create a labelled confusion matrix plot."""
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cm, annot=True, fmt='g', cmap='BuGn', cbar=False,
                ax=ax)
    ax.set_title('Confusion matrix')
    ax.set_xlabel('Predicted')
    ax.set_xticklabels(target_names)
    ax.set_ylabel('Actual')
    ax.set_yticklabels(target_names, fontdict={'verticalalignment': 'center'})


def vader(csv_file):
    df = pd.read_csv(csv_file)
    # Drop unnecessary columns
    df1 = df.drop(['also_buy',
                   'vote',
                   'also_view',
                   'date',
                   'tech1',
                   'tech2',
                   'rank',
                   'feature',
                   'main_cat',
                   'verified',
                   'style',
                   'Rating',
                   'reviewerName',
                   'time',
                   'image_x',
                   'image_y',
                   'description',
                   'category',
                   'title',
                   'price',
                   'brand',
                   'rating_class_num',
                   'review_length',
                   'Unnamed: 0'],
                  axis=1)
    # df1 = df1[:100000]
    print("Value Counts:")
    print(df1['rating_class'].value_counts())
    sid = SentimentIntensityAnalyzer()
    # print(sid.polarity_scores(df1.iloc[0]['review_text']))
    df1['target'] = df1['rating_class'].apply(lambda x: 0 if x == 'bad' else 1)
    df1[['neg', 'neu', 'pos', 'compound']] = df1['clean_text'].apply(
        sid.polarity_scores).apply(pd.Series)
    df1['score'] = df1['compound'].apply(lambda score: 1 if score >= 0 else 0)
    print("This is the Classification Report:")
    print(classification_report(df1['target'], df1['score']))
    print("F1-score:")
    print(
        f1_score(
            df1['target'],
            df1['score'],
            average='micro'))  # using clean text
    print("This is the Classification Matrix:")

    # Plot confusion matrix
    return plot_cm(df1['target'], df1['score'])


def get_word_sentiment(text):
    tokenized_text = nltk.word_tokenize(text)
    pos_word_list = []
    neu_word_list = []
    neg_word_list = []
    sid = SentimentIntensityAnalyzer()
    for word in tokenized_text:
        if sid.polarity_scores(word)["compound"] >= 0.1:
            pos_word_list.append(word)
        elif sid.polarity_scores(word)["compound"] <= -0.1:
            neg_word_list.append(word)
        else:
            neu_word_list.append(word)
    # print('Positive:',pos_word_list)
    words = {
        "Positive": pos_word_list,
        "Neutral": neu_word_list,
        "Negative": neg_word_list,
    }
    return words

    # print('Neutral:',neu_word_list)
    # print('Negative:',neg_word_list)
# get_word_sentiment(df1.iloc[199]['review_text'])
