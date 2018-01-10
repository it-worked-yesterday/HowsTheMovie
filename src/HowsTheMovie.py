from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.request
import random
import tweepy
from configparser import ConfigParser
from textblob.sentiments import PatternAnalyzer
from textblob.sentiments import NaiveBayesAnalyzer
import re, sys, traceback
from scrapy.utils.log import configure_logging
import logging

config = None

def init_app():
	global config 
	global TWEETS_FETCH_COUNT

	#fetching config values from config.ini file
	if config is None:
		config = ConfigParser()
		config.read("../config/config.ini")

	#configuring logging with scrapy
	configure_logging({"LOG_FORMAT": "%(asctime)s [%(levelname)s]: %(message)s"})


class Movie:
	movie_name = ""
	movie_year = ""
	movie_directors = ""
	movie_actors = ""
	movie_rating = ""
	best_rating = ""
	movie_rating_count = ""
	movie_poster = ""
	movie_poster_link = ""

	def __init__(self, *args):
		self.movie_name = args[0]
		self.movie_year = args[1]
		self.movie_directors= args[2]
		self.movie_actors= args[3]
		self.movie_rating= args[4]
		self.best_rating= args[5]
		self.movie_rating_count= args[6]
		self.movie_poster= args[7]
		self.movie_poster_link= args[8]


class TwitterClient:
	o_consumer_key = ""
	o_consumer_secret = ""
	o_access_token = ""
	o_access_secret = ""
	twitter_api_handle = None

	@staticmethod
	def clean_tweet(tweet):
		'''
		Removes links, special characters
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	def __init__(self):
		'''
        establishes connection with twitter and 
        fetches an api handle to call function from tweepy
        '''
		try:
			self.o_consumer_key = config["TWITTER_CRED"]["consumer_key"]
			self.o_consumer_secret = config["TWITTER_CRED"]["consumer_secret"]
			self.o_access_token = config["TWITTER_CRED"]["access_token"]
			self.o_access_secret = config["TWITTER_CRED"]["access_secret"]
			twitter_auth = tweepy.OAuthHandler(self.o_consumer_key, self.o_consumer_secret)
			twitter_auth.set_access_token(self.o_access_token, self.o_access_secret)
			self.twitter_api_handle = tweepy.API(twitter_auth)
		except:
			logging.info ("Twitter Authentication Failed")
			traceback.print_exc()
			return None

	def get_tweets_by_string(self, tweet_string, count):
		'''
        fetches tweets as per the query sting provided
        '''
		return self.twitter_api_handle.search( q = tweet_string, count = count)



class MovieSentimentAnalyzer:
	@staticmethod
	def analyseSentiment(text, analyzer= "NaiveBayesAnalyzer"):
		'''
        Analyses a string using Textblob's sentiment analyzer
        '''
		if analyzer == "NaiveBayesAnalyzer":
			return NaiveBayesAnalyzer().analyze(text)
		elif analyzer == "PatternAnalyzer":
			return PatternAnalyzer().analyze(text)
		else:
			logging.info("Invalid Analyzer")
			return None


def get_movie_details(movie_name):
	'''
	fetches info about a movie by scraping data from IMDB
	using beautiful soup
	'''
	init_app()

	response = {}
	imdb_link = "http://www.imdb.com"

	chrome_options = Options()
	chrome_options.add_argument('--headless')

	#replace <root> with ...well, the project root path 
	driver = webdriver.Chrome(executable_path= "<root>/bin/chromedriver", chrome_options= chrome_options)
	driver.implicitly_wait(10)

	driver.get(imdb_link)
	search_bar = driver.find_element(By.XPATH, '//*[@id="navbar-query"]')
	search_bar.clear()
	search_bar.send_keys(movie_name)
	search_bar.send_keys(Keys.RETURN)

	#driver implicitly waits here
	first_result_a_tag = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/table/tbody/tr[1]/td[2]/a')
	movie_page = first_result_a_tag.get_attribute("href")
	driver.get(movie_page)
	movie_page_html = driver.page_source
	movie_page_soup = BeautifulSoup(movie_page_html, "lxml")

	# fetching title details 
	logging.info("Scraping information about the movie/TV series")
	movie_overview_soup = movie_page_soup.find("div", id = "title-overview-widget")

	movie_name = movie_overview_soup.find("div", class_ = "title_wrapper").find("h1", itemprop ="name").find(text = True, recursive = False).strip()
	
	try:
		movie_year = (((movie_overview_soup.find("div", class_ = "title_wrapper")).find("span", id ="titleYear")).find("a")).text
	except:
		movie_year = None

	movie_directors = "".join([summary.text for summary in movie_overview_soup.find_all("span", itemprop = "director")]).strip()
	movie_actors = [x.strip().strip('\n') for x in "".join([summary.text for summary in movie_overview_soup.find_all("span", itemprop = "actors")]).split(',')]
	movie_rating = ((movie_overview_soup.find ("div", class_ = "ratingValue")).find("span", itemprop = "ratingValue")).text.strip()
	best_rating = ((movie_overview_soup.find ("div", class_ = "ratingValue")).find("span", itemprop = "bestRating")).text
	movie_rating_count = ((movie_overview_soup.find ("div", class_ = "imdbRating")).find("span", itemprop = "ratingCount")).text
	movie_poster = movie_name + " poster.jpg"
	movie_poster_link = movie_overview_soup.find("div", class_ = "poster").img["src"]

	movie = Movie(movie_name, movie_year, movie_directors, movie_actors, movie_rating, best_rating,movie_rating_count,movie_poster,movie_poster_link)
	driver.quit()

	logging.info(vars(movie))
	response["movie"] = vars(movie)
	return response

def get_twitter_sentiments(hashtag):
	'''
	pulls tweets on the given hastag and returns 
	the sentiment analysis around the topic
	'''
	init_app()
	TWEETS_FETCH_COUNT = config.getint("APP","TWEETS_FETCH_COUNT")
	response = {}
	positive_tweets_count, negative_tweets_count = 0,0
	twitter_client = TwitterClient()

	if twitter_client is None:
		logging.info("Could not start the twitter client. Exiting.")
		return
	logging.info("Connected to twitter")

	tweets = twitter_client.get_tweets_by_string('#'+ hashtag,TWEETS_FETCH_COUNT)
	for tweet in tweets:
		if tweet.lang == 'en':
			#cleaning the tweet to remove links, special characters
			#this shorts the input for sentiment analyzer
			clean_tweet_text = TwitterClient.clean_tweet(tweet = tweet.text)
			sentiments = MovieSentimentAnalyzer.analyseSentiment(text = clean_tweet_text,  analyzer = "NaiveBayesAnalyzer")
			logging.info(clean_tweet_text)
			logging.info(sentiments)

			if (sentiments[1] > sentiments[2]) and (sentiments[1] > 0.3) :
				positive_tweets_count += 1			
				logging.info ("positive" )
			elif (sentiments[2] > sentiments[1]) and (sentiments[2] > 0.3) :
				negative_tweets_count += 1
				logging.info ("negative")
			else:
				logging.info ("neutral")

	response["total_review"] = len(tweets) 
	response["positive_reviews"] = 100 * positive_tweets_count / len(tweets) 
	response["negative_reviews"] = 100 * negative_tweets_count / len(tweets) 
	
	logging.info("Out of a total of %d tweets:" % len(tweets) )
	logging.info("Positive tweets: "+ str(response["positive_reviews"]))
	logging.info("Negative tweets: "+ str(response["negative_reviews"]))

	return response