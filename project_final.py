import re 
import os
import tweepy 
from flask import Flask,render_template,request
import requests
from tweepy import OAuthHandler 
from textblob import TextBlob 
from textblob.translate import Translator
app = Flask('__name__')
class TwitterClient(object): 
	
	def __init__(self): 

		consumer_key = os.environ.get("consumer_key")
		consumer_secret = os.environ.get("consumer_secret")
		access_token = os.environ.get("access_token")
		access_token_secret = os.environ.get("access_token_secret")

		try: 
			
			self.auth = OAuthHandler(consumer_key, consumer_secret) 
			
			self.auth.set_access_token(access_token, access_token_secret) 
		
			self.api = tweepy.API(self.auth) 
		except: 
			print("Error: Authentication Failed") 

	def clean_tweet(self, tweet): 
	
		 # wthout clean
		 #print("======>",tweet)
		 #t = Translator()
		 #tweet = t.translate(tweet,"auto",'en')
		 clean = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
		
		
		 # clean tweets
		 #print("----->",clean)
		 # to toknise tweets by words	
		 #print(list(clean.split()))
		
		 return clean
		
		
	def get_tweet_sentiment(self, tweet): 
		
		
		analysis = TextBlob(self.clean_tweet(tweet)) 
		
		
		
		
		# to print all words with tag means label every word as part of speech 
		#print(analysis.tags)
		
		# toknise tweets word by word
		#print(analysis.words)
		#print("polarity of text:->",analysis.sentiment.polarity)
		
		# tokenise by sentence by sentence.
		#print(analysis.sentences)
		
		
		# use >= to add neutral tweets to positive tweets
		if analysis.sentiment.polarity > 0: 
			return 'positive'
		# comment below 2 line to ADD neutral in negative 
		elif analysis.sentiment.polarity == 0: 
			return 'neutral'
		else: 
			return 'negative'

	def get_tweets(self, query, count): 
		
		
		tweets = [] 

		try: 
			fetched_tweets = self.api.search(q = query, count = count) 
			#print(fetched_tweets)
			for tweet in fetched_tweets: 
				parsed_tweet = {}
				parsed_tweet['text'] = tweet.text 
				# to print tweets only
				#print(tweet.text)
				parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

			
				if tweet.retweet_count > 0: 
					
					if parsed_tweet not in tweets: 
						tweets.append(parsed_tweet) 
				else: 
					tweets.append(parsed_tweet) 
			#print(tweets)
			return tweets 

		except tweepy.TweepError as e: 
			
			print("Error : " + str(e)) 
  			


api = TwitterClient() 
@app.route('/', methods=['POST', "GET"])
def index():
	if request.method =="GET":
		return render_template('input.html')
	else:
		search_keyword=request.form.get('keyword')
		tweets = api.get_tweets(query = search_keyword, count = 300)


		ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 

		#print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 

		pt=100*len(ptweets)/len(tweets)
		pt = round(pt,2)
		ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 

		#print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
		nt=100*len(ntweets)/len(tweets)
		nt=round(nt,2)
		otweets=[tweet for tweet in tweets if tweet['sentiment'] == 'neutral'] 
		#print("Neutral tweets percentage: {} %".format(100*(len(tweets) -len(ntweets) - len(ptweets))/len(tweets))) 
		ot=100*(len(tweets) -len(ntweets) - len(ptweets))/len(tweets)
		ot=round(ot,2)
		return render_template("result.html",positive=pt,negative=nt,neutral=ot,keyword=search_keyword,ptweets=ptweets,ntweets=ntweets,otweets=otweets)
		


		

	#print("\n\nPositive tweets:") 
	#for tweet in ptweets[:10]: 
		#print(tweet['text']) 


	#print("\n\nNegative tweets:") 
	#for tweet in ntweets[:10]: 
		#print(tweet['text']) 
	# https://pdfs.semanticscholar.org/c114/7f3d9b46ff0a0c7c43b668123cb15a26120d.pdf

