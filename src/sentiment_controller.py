import logging

from src.sentiment_pipeline import SentimentPipeline

logger = logging.getLogger(__name__)


class SentimentController:
    """
    A class that provides methods to control the sentiment analysis on documents in the MongoDB database.
    """

    def __init__(self, db_client):
        """
        Initialize the SentimentController.
        """
        self.db_client = db_client
        self.sentiment_pipeline = SentimentPipeline()

    def write_sentiments_to_documents(self, collection, field_to_analyze):
        """
        Writes the sentiment score and label to the documents in the specified collection.

        :param collection: The name of the collection to write the sentiment to.
        :param field_to_analyze: The name of the field in the collection to analyze.
        """
        from concurrent.futures import ThreadPoolExecutor

        def process_document(document):
            sentiment = self.sentiment_pipeline.get_tokenized_sentiment(data=document[field_to_analyze],
                                                                        collection=collection)
            # update current document with sentiment
            db_client.update_data_by_id(collection, document['_id'], {'sentiment': sentiment})

            logger.info(
                f'Updated {document["_id"]} with Sentiment Score {sentiment["score"]} and Sentiment Label {sentiment["label"]}.'
            )

        with self.db_client as db_client:
            documents = list(db_client.db[collection].find())
            with ThreadPoolExecutor() as executor:
                executor.map(process_document, documents)
