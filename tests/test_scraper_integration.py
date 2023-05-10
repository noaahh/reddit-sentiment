import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.config import DRIVER_OPTIONS, POSTS_COLLECTION, COMMENTS_COLLECTION
from src.database import connect_to_db, close_db_connection, get_data
from src.scraper import SubredditScraper
from src.utils import get_driver, handle_cookie_banner
from tests.test_constants import TEST_SUBREDDIT_ID, TEST_DATABASE_NAME, TEST_SCROLL_TIME


class TestScraperIntegration(unittest.TestCase):

    def setUp(self):
        self.scraper = SubredditScraper(DRIVER_OPTIONS)
        self.client, self.db = connect_to_db(TEST_DATABASE_NAME)

    def test_subreddit_page_load(self):
        with get_driver(DRIVER_OPTIONS) as driver:
            driver.get(self.scraper.get_subreddit_url(TEST_SUBREDDIT_ID))
            WebDriverWait(driver, 10).until(EC.url_matches(r"https://www.reddit.com/r/.*"))
            handle_cookie_banner(driver)

            subreddit_title_element = driver.find_element(By.XPATH, "//h1[contains(@class, '_2yYPPW47QxD4lFQTKpfpLQ')]")

            self.assertIsNotNone(subreddit_title_element)
            self.assertIn("python", subreddit_title_element.text.lower())

    def test_scraping(self):
        self.scraper.scrape_subreddit(TEST_SUBREDDIT_ID, max_posts=1)

        # Check if the posts were saved to the database
        posts = get_data(POSTS_COLLECTION, {"subreddit": TEST_SUBREDDIT_ID})
        self.assertGreater(len(posts), 0)

        # Check if the comments were saved to the database
        comments = get_data(COMMENTS_COLLECTION, {})
        self.assertGreater(len(comments), 0)

    def tearDown(self):
        self.scraper = None
        self.client.drop_database(TEST_DATABASE_NAME)
        close_db_connection()


if __name__ == "__main__":
    unittest.main()