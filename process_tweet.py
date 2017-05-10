import nltk
import re
import csv
import json
import random
from sklearn.linear_model import LogisticRegression
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from collections import Counter
import pickle
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer

featureList = []
stopWords = []


def vader_scores(text):
    sid = SentimentIntensityAnalyzer()
    return sid.polarity_scores(text)


def _processTweet(tweet):
    # Convert to lower case
    tweet = tweet.lower()
    # Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    # Convert @username to AT_USER
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # trim
    tweet = tweet.strip('\'"')
    return tweet


def _replaceTwoOrMore(s):
    # look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)


def _getStopWordList(stopWordListFileName):
    # read the stopwords file and build a list
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords


def _getFeatureVector(tweet):
    global stopWords
    featureVector = []
    # split tweet into words
    words = tweet.split()
    for w in words:
        # replace two or more with two occurrences
        w = _replaceTwoOrMore(w)
        # strip punctuation
        w = w.strip('\'"?,.')
        # check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        # ignore if it is a stop word
        if (w in stopWords):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector


def _extractFeatures(tweet):
    tweet_words = set(tweet[0])
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    features['vader_pos'] = int(tweet[1]['pos'] * 5)
    features['vader_neg'] = int(tweet[1]['neg'] * 5)
    features['vader_neu'] = int(tweet[1]['neu'] * 5)
    return features


def perform_analysis(training_set):
    random.shuffle(training_set)
    split_num = int(len(training_set) * 0.8)

    tr_set = training_set[:split_num]
    te_set = training_set[split_num:]
    # tr_set = training_set
    # te_set = training_set

    # Train the classifier
    NBClassifier = nltk.NaiveBayesClassifier.train(tr_set)
    print(nltk.classify.accuracy(NBClassifier, te_set))

    LRClassifier = SklearnClassifier(LogisticRegression())
    LRClassifier.train(tr_set)
    print(nltk.classify.accuracy(LRClassifier, te_set))

    RFClassifier = SklearnClassifier(RandomForestClassifier())
    RFClassifier.train(tr_set)
    print(nltk.classify.accuracy(RFClassifier, te_set))

    SVCClassifier = SklearnClassifier(LinearSVC())
    SVCClassifier.train(tr_set)
    print(nltk.classify.accuracy(SVCClassifier, te_set))

    total = 0
    correct = 0
    c_positive = 0
    c_neutral = 0
    c_negative = 0

    for t_ex in te_set:
        c = SVCClassifier.classify(t_ex[0])
        if c == 'positive':
            c_positive += 1
        elif c == 'neutral':
            c_neutral += 1
        else:
            c_negative += 1

        if c == t_ex[1]:
            correct += 1
        total += 1

    print("Total: %d, Correct: %d, Classified positive: %s, Classified neutral: %s, Classified negative: %s" % (
        total, correct, c_positive, c_neutral, c_negative))


def train():
    global stopWords
    global featureList
    # get the file name of traning dataset from config.json
    config = json.load(open('config.json', 'r'))
    trainDataFile = config['train_data_file']
    inpTweets = csv.reader(open(trainDataFile, 'r'))
    stopWords = _getStopWordList('stopwords.txt')

    # Get tweet words
    tweets = []
    for row in inpTweets:
        sentiment = row[1]
        tweet = row[0]
        processedTweet = _processTweet(tweet)
        featureVector = _getFeatureVector(processedTweet)
        featureList.extend(featureVector)
        tweets.append(((featureVector, vader_scores(tweet)), sentiment))
    # print tweets
    # Remove featureList duplicates

    featureList = Counter(featureList).most_common(10000)

    featureList = [word[0] for word in featureList if word[1] >= 0 and len(word[0]) >= 0]

    print(len(featureList))

    # Extract feature vector for all tweets in one shote
    training_set = nltk.classify.util.apply_features(_extractFeatures, tweets)

    training_set = list(training_set)

    perform_analysis(training_set)

    SVCClassifier = SklearnClassifier(LinearSVC())
    SVCClassifier.train(training_set)

    return SVCClassifier


def tag(NBClassifier, tweet):
    processedTweet = _processTweet(tweet)
    return NBClassifier.classify(_extractFeatures((_getFeatureVector(processedTweet), vader_scores(tweet))))


def get_classifier():
    global stopWords, featureList
    pickle_classifier = 'classifier.pickle'

    if os.path.isfile(pickle_classifier):
        pickle_file = open(pickle_classifier, "rb")
        (classifier, stopWords, featureList) = pickle.load(pickle_file)
        pickle_file.close()
        return classifier

    classifier = train()

    pickle_file = open(pickle_classifier, "wb")
    pickle.dump((classifier, stopWords, featureList), pickle_file)
    pickle_file.close()
    return classifier


def test():
    NBClassifier = get_classifier()
    print(tag(NBClassifier, "what a wonderful day :)"))
    print(tag(NBClassifier, "I hate the weather"))
    print(tag(NBClassifier, "today is bad :("))


def get_sentiment(text):
    NBClassifier = get_classifier()
    return tag(NBClassifier, text)



