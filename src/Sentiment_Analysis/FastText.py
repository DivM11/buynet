import fasttext
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.utils import resample
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
import seaborn as sns

removal = [
    'also_buy',
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
    'Unnamed: 0',
]


# Create function so that we could reuse later

def plot_cm(
    y_test,
    y_pred,
    target_names=['bad', 'good'],
    figsize=(5, 3),
):
    """Create a labelled confusion matrix plot."""

    cm = confusion_matrix(y_test, y_pred)
    (fig, ax) = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm,
        annot=True,
        fmt='g',
        cmap='BuGn',
        cbar=False,
        ax=ax,
    )
    ax.set_title('Confusion matrix')
    ax.set_xlabel('Predicted')
    ax.set_xticks(np.arange(len(target_names)))
    ax.set_xticklabels(target_names)
    ax.set_ylabel('Actual')
    ax.set_yticks(np.arange(len(target_names)))
    ax.set_yticklabels(target_names,
                       fontdict={'verticalalignment': 'center'})


def fasttext_default(csv_file):
    df = pd.read_csv(csv_file)
    df2 = df.drop(removal, axis=1)

    # df2 = df2[:100000]

    X = df2['clean_text']
    y = df2['rating_class']

    # Without resampling

    # Split into train-test sets.

    (X_train, X_test, y_train, y_test) = train_test_split(
        X, y, stratify=y, test_size=0.33)
    (X_train, X_val, y_train, y_val) = train_test_split(
        X_train, y_train, stratify=y_train, test_size=0.20)

    # FastText input files needs to be in text files with each line prepended
    # with '__label__'+'<label name>'

    with open('./test.txt', 'w') as test_file_handler:
        for (X_test_entry, y_test_entry) in zip(X_test, y_test):
            line_to_write = '__label__' + str(y_test_entry) + '\t' \
                + str(X_test_entry) + '\n'
            try:
                test_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Test File Written')

    with open('./val.txt', 'w') as val_file_handler:
        for (X_val_entry, y_val_entry) in zip(X_val, y_val):
            line_to_write = '__label__' + str(y_val_entry) + '\t' \
                + str(X_val_entry) + '\n'
            try:
                val_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Val File Written')

    # Write the train file.

    with open('./train.txt', 'w') as train_file_handler:
        for (X_train_entry, y_train_entry) in zip(X_train, y_train):
            line_to_write = '__label__' + str(y_train_entry) + '\t' \
                + str(X_train_entry) + '\n'
            try:
                train_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Train File Written')

    # These files are in the required format of Fasttext

    model = fasttext.train_supervised(input='./train.txt', epoch=25)
    print(
        'Validation set Sample number, Precision, Recall:{}'.format(
            model.test('./val.txt')))
    print(
        'Test set Sample number, Precision, Recall:{}'.format(
            model.test('./test.txt')))
    model.save_model('model_fasttext.bin')

    # model = fasttext.load_model("model_fasttext.bin")

    # FastText model.predict supports only 1 line so iterating through each
    # line to get prediction array

    c = []
    f = open('test.txt', 'r')
    for line in f.readlines():
        (d, l) = model.predict(line[:-1])
        c.append(int(d[0][9]))

    y_pred = pd.Series(c)

    # Plot confusion matrix
    print(confusion_matrix(y_test, y_pred))

    plot_cm(y_test, y_pred)
    m = f1_score(y_test, y_pred)

    return m


# Upsampling

def fasttext_upsample(csv_file, majority_class_samples):
    df = pd.read_csv(csv_file)
    df2 = df.drop(removal, axis=1)

    data = df2[['clean_text', 'rating_class']]

    data['rating_class'] = data['rating_class'].apply(
        lambda score: (1 if score == 'good' else 0))

    y = data['rating_class']
    X = data['clean_text']

    # Here X_train from original data separated

    (X_train, X_test, y_train, y_test) = train_test_split(
        X, y, stratify=y, test_size=0.33)

    dat = {'clean_text': X_train, 'rating_class': y_train}
    df_imbalance = pd.DataFrame(dat)

    # this is imabalanced data on which Upsampling will be done and Validation
    # set will also be extracted

    print('Class value counts:')
    print(df_imbalance['rating_class'].value_counts())

    df_majority = df_imbalance[df_imbalance['rating_class'] == 1]
    df_minority = df_imbalance[df_imbalance['rating_class'] == 0]

    # Upsample minority class

    df_minority_upsampled = resample(
        df_minority,
        replace=True,
        n_samples=majority_class_samples,
        random_state=123)  # sample with replacement

    # to match majority class
    # reproducible results

    # Combine majority class with upsampled minority class

    df_upsampled = pd.concat([df_majority, df_minority_upsampled])

    # Display new class counts

    df_upsampled['rating_class'].value_counts()

    y_ups = df_upsampled['rating_class']
    X_ups = df_upsampled['clean_text']

    (X_train, X_val, y_train, y_val) = train_test_split(
        X_ups, y_ups, stratify=y_ups, test_size=0.20)

    # write the test file

    with open('./test.txt', 'w') as test_file_handler:
        for (X_test_entry, y_test_entry) in zip(X_test, y_test):
            line_to_write = '__label__' + str(y_test_entry) + '\t' \
                + str(X_test_entry) + '\n'
            try:
                test_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Test File Written')

    # write the val file

    with open('./val.txt', 'w') as val_file_handler:
        for (X_val_entry, y_val_entry) in zip(X_val, y_val):
            line_to_write = '__label__' + str(y_val_entry) + '\t' \
                + str(X_val_entry) + '\n'
            try:
                val_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Val File Written')

    # Write the train file.

    with open('./train.txt', 'w') as train_file_handler:
        for (X_train_entry, y_train_entry) in zip(X_train, y_train):
            line_to_write = '__label__' + str(y_train_entry) + '\t' \
                + str(X_train_entry) + '\n'
            try:
                train_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Train File Written')

    model = fasttext.train_supervised(input='./train.txt')  # , epoch=25)

    print(
        'Upsampled Validation set Sample number, Precision, Recall:{}'.format(
            model.test('./val.txt')))

    print(
        'Original Test set Sample number, Precision, Recall:{}'.format(
            model.test('./test.txt')))

    model.save_model('model_fasttext.bin')

    # model = fasttext.load_model("model_fasttext.bin")

    # FastText model.predict supports only 1 line so iterating through each
    # line to get prediction array

    c = []
    f = open('test.txt', 'r')
    for line in f.readlines():
        (d, l) = model.predict(line[:-1])
        c.append(int(d[0][9]))

    y_pred = pd.Series(c)

    # Plot confusion matrix
    print(confusion_matrix(y_test, y_pred))

    plot_cm(y_test, y_pred)

    m = f1_score(y_test, y_pred)

    return m


# Downsampling

def fasttext_downsample(csv_file, minority_class_samples):
    df = pd.read_csv(csv_file)
    df2 = df.drop(removal, axis=1)

    data = df2[['clean_text', 'rating_class']]

    data['rating_class'] = data['rating_class'].apply(
        lambda score: (1 if score == 'good' else 0))

    y = data['rating_class']
    X = data['clean_text']

    # Here X_train from original data separated

    (X_train, X_test, y_train, y_test) = train_test_split(
        X, y, stratify=y, test_size=0.33)

    dat = {'clean_text': X_train, 'rating_class': y_train}
    df_imbalance = pd.DataFrame(dat)

    # this is imabalanced data on which Upsampling will be done and Validation
    # set will also be extracted

    print('Class value counts:')
    print(df_imbalance['rating_class'].value_counts())
    df_majority = df_imbalance[df_imbalance['rating_class'] == 1]
    df_minority = df_imbalance[df_imbalance['rating_class'] == 0]

    # Downsample majority class

    df_majority_downsampled = resample(
        df_majority,
        replace=False,
        n_samples=minority_class_samples,
        random_state=123)  # sample with replacement

    # to match majority class
    # reproducible results

    # Combine majority class with upsampled minority class

    df_downsampled = pd.concat([df_minority, df_majority_downsampled])

    # Display new class counts

    df_downsampled['rating_class'].value_counts()

    y_downs = df_downsampled['rating_class']
    X_downs = df_downsampled['clean_text']

    (X_train, X_val, y_train, y_val) = train_test_split(
        X_downs, y_downs, stratify=y_downs, test_size=0.20)

    # write the test file

    with open('./test.txt', 'w') as test_file_handler:
        for (X_test_entry, y_test_entry) in zip(X_test, y_test):
            line_to_write = '__label__' + str(y_test_entry) + '\t' \
                + str(X_test_entry) + '\n'
            try:
                test_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Test File Written')

    # write the val file

    with open('./val.txt', 'w') as val_file_handler:
        for (X_val_entry, y_val_entry) in zip(X_val, y_val):
            line_to_write = '__label__' + str(y_val_entry) + '\t' \
                + str(X_val_entry) + '\n'
            try:
                val_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Val File Written')

    # Write the train file.

    with open('./train.txt', 'w') as train_file_handler:
        for (X_train_entry, y_train_entry) in zip(X_train, y_train):
            line_to_write = '__label__' + str(y_train_entry) + '\t' \
                + str(X_train_entry) + '\n'
            try:
                train_file_handler.write(line_to_write)
            except BaseException:
                print(line_to_write)
                break
    print('Train File Written')

    model = fasttext.train_supervised(input='./train.txt', epoch=20)

    print(
        'Downsampled Validation set Sample number, Precision, Recall:{}'.format
        (model.test('./val.txt')))

    print(
        'Original Test set Sample number, Precision, Recall:{}'.format(
            model.test('./test.txt')))

    model.save_model('model_fasttext.bin')

    # model = fasttext.load_model("model_fasttext.bin")

    # FastText model.predict supports only 1 line so iterating through each
    # line to get prediction array

    c = []
    f = open('test.txt', 'r')
    for line in f.readlines():
        (d, l) = model.predict(line[:-1])
        c.append(int(d[0][9]))

    y_pred = pd.Series(c)

    # Plot confusion matrix
    print(confusion_matrix(y_test, y_pred))

    plot_cm(y_test, y_pred)

    m = f1_score(y_test, y_pred)

    return m
