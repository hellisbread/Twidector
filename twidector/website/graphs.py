from socket import has_dualstack_ipv6
from tkinter import E
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import validation_curve
import matplotlib.pyplot as plt
import base64
from io import StringIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
import pandas as pd
from website.fakenews import *
from website.hatedetection import *
from nltk.stem import WordNetLemmatizer
import contractions
import numpy as np

def get_graph():

  global df
  global vectorizer, x_train, x_test, x_train_vec, y_train , SVM
  
  df = pd.read_csv('hateDetection.csv')
  clean_Tweets = df["tweet"]
  df['clean_tweet'] = clean_Tweets
  #split dataset into training and testing
  y = df["class"].values

  x = df["clean_tweet"].values
  # hu = vectorizer.fit(x)

  x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, test_size=0.2)

  # learn a vocabulary dictionary of all tokens in the raw documents
  vectorizer.fit(list(x_train) + list(x_test))

  x_transformed = vectorizer.transform(x)
  param_range = [0.05, 0.1 , 0.5, 1]
  model_for_validation = LinearSVC(C = 0.8)
  train_scores, test_scores = validation_curve(model_for_validation, x_transformed, y, param_name="C", param_range = param_range, cv = 5 , scoring = "accuracy")

  train_scores_mean = np.mean(train_scores, axis=1)
  train_scores_std = np.std(train_scores, axis=1)
  test_scores_mean = np.mean(test_scores, axis=1)
  test_scores_std = np.std(test_scores, axis=1)
  plt.switch_backend('AGG')
  # plt.figure(figsize(10,5))
  plt.title("Validation Curve with SVM")
  plt.xlabel("C")
  plt.ylabel("Score")
  plt.ylim(0.0, 1.1)

  plt.semilogx(
        param_range, train_scores_mean, label="Training score", color="darkorange", lw=2
    )

  plt.fill_between(
        param_range,
        train_scores_mean - train_scores_std,
        train_scores_mean + train_scores_std,
        alpha=0.2,
        color="darkorange",
        lw=2,
    )

  plt.semilogx(
        param_range, test_scores_mean, label="Cross-validation score", color="navy", lw=2
    )

  plt.fill_between(
        param_range,
        test_scores_mean - test_scores_std,
        test_scores_mean + test_scores_std,
        alpha=0.2,
        color="navy",
        lw=2,
    )
  plt.legend(loc="best")
  plt.show()

  buffer = StringIO()
  plt.savefig(buffer, format="svg")
  buffer.seek(0)
  image_png = buffer.getvalue()
  # graph = base64.b64encode(image_png)
  # graph = graph.decode('utf-8') 
  buffer.close()
  return image_png

#fakenews graph + accuracy score 
# df = pd.read_csv("fakenewscleaned.csv", encoding = "ISO-8859-1")
# df = df.dropna()
# count = 0

def cleanStatements(Statements):
    tempArr = []
    #clean the data
    #remove numbers, urls, additional whitespaces and puntuation
    for statement in Statements:
        new_statement = statement.lower()
        new_statement = contractions.fix(new_statement)
        new_statement = re.sub(r'[0-9]+', '', new_statement)
        new_statement = re.sub(r'http\S+', '', new_statement)
        new_statement = re.sub(r'[^\w\s]', '', new_statement)
        new_statement = re.sub(r'\s+', ' ', new_statement)

    #lemmatization and stopwords process
        count_token = 0
        seperator = " "
        stringArr = []
        lem = WordNetLemmatizer()
        tokenization = nltk.word_tokenize(new_statement)
        stop_words = set(stopwords.words('english'))
        for w in tokenization:
            clean_word = lem.lemmatize(w , pos="v")
            if clean_word not in stop_words:
                stringArr.append(clean_word)
            if(count_token == len(tokenization) - 1):
                str = seperator.join(stringArr)
                tempArr.append(str)
                stringArr = []
            count_token += 1
    return tempArr
    
# clean_statements = cleanStatements(df["Statement"])
# df['Clean_Statements'] = clean_statements
# df["Label"].value_counts()


# #split the data into train and test set
# y = df['Label'].values
# x = df['Clean_Statements'].values
# x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, test_size=0.2)

# #fit and transform data into a matrix
# vectorizer = TfidfVectorizer(ngram_range = (1 , 3), max_features = 1000)
# vectorizer.fit(list(x_train) + list(x_test))
# x = vectorizer.fit_transform(x)
# x_train_vec = vectorizer.fit_transform(x_train)
# x_test_vec = vectorizer.fit_transform(x_test)
# vectorizer.get_feature_names_out()

#Test and predict the data
def predictStatement(statements):
    model = LinearSVC(C = 0.05)
    model.fit(x_train_vec, y_train)
    cleanSentence = cleanStatements(statements)
    sentence_vec = vectorizer.transform(cleanSentence)
    pred = model.predict(sentence_vec)
    return (pred)

def fakenews_graph():
  #fit and transform data into a matrix
  vectorizer = TfidfVectorizer(ngram_range = (1 , 3), max_features = 1000)
  vectorizer.fit(list(x_train) + list(x_test))
  vectorizer.get_feature_names_out() 
  #validation curve to assess overfit and underfit
  param_range = np.arange(0 , 10)
  model_for_validation = LinearSVC(C=0.05)
  train_scores, test_scores = validation_curve(model_for_validation, x, y, param_name="C", param_range = param_range, cv = 5 , scoring = "accuracy")

  train_scores_mean = np.mean(train_scores, axis=1)
  train_scores_std = np.std(train_scores, axis=1)
  test_scores_mean = np.mean(test_scores, axis=1)
  test_scores_std = np.std(test_scores, axis=1)

  plt.switch_backend('AGG')
  plt.title("Validation Curve with SVM")
  plt.xlabel("C")
  plt.ylabel("Score")
  plt.ylim(0.0, 1.1)

  plt.semilogx(
      param_range, train_scores_mean, label="Training score", color="darkorange", lw=2
  )

  plt.fill_between(
      param_range,
      train_scores_mean - train_scores_std,
      train_scores_mean + train_scores_std,
      alpha=0.2,
      color="darkorange",
      lw=2,
  )

  plt.semilogx(
      param_range, test_scores_mean, label="Cross-validation score", color="navy", lw=2
  )
  plt.fill_between(
      param_range,
      test_scores_mean - test_scores_std,
      test_scores_mean + test_scores_std,
      alpha=0.2,
      color="navy",
      lw=2,
  )

  plt.legend(loc="best")
  plt.show()

  buffer = StringIO()
  plt.savefig(buffer, format="svg")
  buffer.seek(0)
  fn_img = buffer.getvalue()
  buffer.close()
  return fn_img



def train_FN_Model():
    
    global FN_vectorizer
    global linear_model
    
    y = df['Label'].values
    x = df['Clean_Statements'].values
    x_train, x_test, y_train, y_test = train_test_split(x, y, stratify = y, test_size=0.2)
    
    #fit into bag of words and transform data into a matrix
    FN_vectorizer = TfidfVectorizer(ngram_range = (1 , 3), max_features = 2000)
    FN_vectorizer.fit(list(x_train) + list(x_test))
    
    x_train_vec = FN_vectorizer.transform(x_train)
    x_test_vec = FN_vectorizer.transform(x_test)
    
    #fit the matrix data into the SVC model
    linear_model = LinearSVC(C = 0.05)
    linear_model.fit(x_train_vec, y_train)
    prediction = linear_model.predict(x_test_vec)
    score = accuracy_score(y_test, prediction) * 100
    return score



#fake news graph
def fn_graph():
  fk_news = df["Label"].value_counts()
  print(fk_news)
  false_news = fk_news[0]
  true_news = fk_news[1]

  return [false_news, true_news]

def scores(filename):
    
    df = pd.read_csv(filename)
    df = df.dropna()
    y = df['Label'].values
    x = df['text'].values
    print("y:")
    print(y)

    expected_value = predictStatement(x)
    print("expected_value")
    print(expected_value)
    
    return(accuracy_score(expected_value,y)*100)



    





