import os
import pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re


class LR_Model:
    model = pickle.load(open(os.path.join("static/model/lr_model.pkl"), "rb"))

    def get_stopwords_list(stop_file_path):
        with open(os.path.join(stop_file_path), "r", encoding="utf-8") as f:
            stopwords = f.readlines()
            stop_set = set(m.strip() for m in stopwords)
            return list(frozenset(stop_set))

    malay_stop_word = get_stopwords_list("static/model/malay_stop_word.txt")

    def preprocess_text(self, text):
        # remove non alphabetic
        non_alphabetic = re.sub("[^A-Za-z]+", " ", text)

        # tokenize
        tokens = word_tokenize(non_alphabetic.lower())

        # remove stop words in malay and english
        filtered_tokens = [
            token for token in tokens if token not in self.malay_stop_word
        ]
        filtered_tokens = [
            filtered_tokens
            for filtered_tokens in filtered_tokens
            if filtered_tokens not in stopwords.words("english")
        ]

        return " ".join(filtered_tokens)

    def predict(self, text):
        vectorizer = pickle.load(open(os.path.join("static/model/fit_tfidf.pkl"), "rb"))
        tf_x_input = vectorizer.transform([self.preprocess_text(text)])
        y_predict = self.model.predict(tf_x_input)

        return y_predict[0]
