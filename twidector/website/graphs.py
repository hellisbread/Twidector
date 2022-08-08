from socket import has_dualstack_ipv6
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import validation_curve
import matplotlib.pyplot as plt
import base64
from io import StringIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
import pandas as pd
from website.hatedetection import *

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




