import json
import requests
import base64

from datetime import datetime, timedelta

from stop_words import stop_words

base_url = 'https://api.twitter.com/'

def read_credentials():
	file = open("creds.txt","r")
	credentials = file.readlines()
	creds = {
		'api_key' : credentials[0].rstrip(),
		'api_secret' : credentials[1].rstrip(),
		'token' : credentials[2].rstrip(),
		'token_secret' : credentials[3].rstrip()
	}
	file.close()
	return creds

def get_bearer_token():
	creds = read_credentials()
	key_secret = '{}:{}'.format(creds['api_key'], creds['api_secret']).encode('ascii')
	b64_encoded_key = base64.b64encode(key_secret)
	b64_encoded_key = b64_encoded_key.decode('ascii')

	auth_url = '{}oauth2/token'.format(base_url)

	auth_headers = {
    	'Authorization': 'Basic {}'.format(b64_encoded_key),
    	'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
	}

	auth_data = {
    	'grant_type': 'client_credentials'
	}

	auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
	return auth_resp.json()['access_token']

def tweets_of_last_hour():
	bearer = get_bearer_token()
	search_url = '{}1.1/search/tweets.json'.format(base_url)

	search_headers = {
 	   'Authorization': 'Bearer {}'.format(bearer)
	}

	search_params = {
		'q' : '#Canucks',
		'result_type' : 'recent',
		'count' : 100	# 100 is max
	}

		
	search_resp = requests.get(search_url, headers=search_headers, params=search_params)
	new_tweet_data = search_resp.json()['statuses']
	tweet_data = []

	while within_an_hour(new_tweet_data[-1]):
		search_params['max_id'] = get_max_id(new_tweet_data)
		search_resp = requests.get(search_url, headers=search_headers, params=search_params)
		tweet_data.extend(new_tweet_data)
		new_tweet_data = search_resp.json()['statuses']

	while not within_an_hour(new_tweet_data[-1]):
		new_tweet_data.pop(-1)
	tweet_data.extend(new_tweet_data)

	print(len(tweet_data))
	return tweet_data

def get_max_id(tweet_data):
	max_id = 0
	for x in tweet_data:
		if max_id < x['id']:
			max_id = x['id']
	return max_id

def within_an_hour(tweet):
	tweet_dt = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
	return tweet_dt > (datetime.now() - timedelta(hours = 1))

def process_data(tweet_data):
	processed_data = {}

	word_counts = {}
	mentioned_counts = {}
	user_post_counts = {}
	
	for tweet in tweet_data:
		# Collect most common words
		for word in tweet['text'].split(' '):
			lower_word = word.lower()
			if lower_word in stop_words or '@' in lower_word:
				continue
			elif lower_word in word_counts:
				word_counts[lower_word] = word_counts[lower_word] + 1
			else:
				word_counts[lower_word] = 1
		
		# Get most mentioned user
		for user in tweet['entities']['user_mentions']:
			user_name = user['screen_name']
			if user_name in mentioned_counts:
				mentioned_counts[user_name] = mentioned_counts[user_name] + 1
			else:
				mentioned_counts[user_name] = 1

		# Get most active user
		for x in tweet_data:
			user_name = tweet['user']['screen_name']
			if user_name in user_post_counts:
				user_post_counts[user_name] = user_post_counts[user_name] + 1
			else:
				user_post_counts[user_name] = 1

	processed_data['word_counts'] = word_counts
	processed_data['mentioned_counts'] = mentioned_counts
	processed_data['user_post_counts'] = user_post_counts
	return processed_data


def get_most_common_word(data):
	counts = data['word_counts']
	return max(counts, key=counts.get)

def get_most_mentioned_user(data):
	counts = data['mentioned_counts']
	return max(counts, key=counts.get)

def get_most_active_user(data):
	counts = data['user_post_counts']
	return max(counts, key=counts.get)

tweet_data = tweets_of_last_hour()
pdata = process_data(tweet_data)
print(get_most_common_word(pdata))
print(get_most_mentioned_user(pdata))
print(get_most_active_user(pdata))
