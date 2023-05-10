import re

import numpy as np
from scipy.special import softmax
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig

from src.config import COMMENTS_COLLECTION, SENTIMENT_MODEL, POSTS_COLLECTION


class SentimentPipeline:

    def __init__(self, model_path=SENTIMENT_MODEL):
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.config = AutoConfig.from_pretrained(self.model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)

    def get_tokenized_sentiment(self, data, collection=COMMENTS_COLLECTION):
        text = self.preprocess(data, type=collection)
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        ranking = np.argsort(scores)[::-1]
        return {
            'label': self.config.id2label[ranking[0]],
            'score': np.round(float(scores[ranking[0]]), 4)
        }

    @staticmethod
    def preprocess(text, type):
        patterns = [
            (r'u\/[\w\d\-_]+', 'user'),
            (r'r\/[\w\d\-_]+', 'subreddit'),
            (r'\bhttps?:\/\/[^\s]+\b', 'link')
        ]

        if type == POSTS_COLLECTION:
            text.replace("_", " ")

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)

        return text
