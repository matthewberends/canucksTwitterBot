import json
import requests
import base64

api_key = "tTT9c3dseV2JoVWicvYUvcxuc"
api_secret = "Sn6ydlKaCkFcGSfghMywolRKmw4ajlozZkCdcboO6sL3co5QQb"
token = "1267289327710552067-xRr2JrtWu1IkyVp5zyS3tgX6p1Eohl"
token_secret = "1267289327710552067-xRr2JrtWu1IkyVp5zyS3tgX6p1Eohl"

base_url = 'https://api.twitter.com/'

def get_bearer_token():
	key_secret = '{}:{}'.format(api_key, api_secret).encode('ascii')
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
	print(auth_resp.json()['access_token'])
	return auth_resp.json()['access_token']

def get_canuck_tweets():
	bearer = get_bearer_token()
	search_headers = {
 	   'Authorization': 'Bearer {}'.format(bearer)    
	}

	search_params = {
    	'q': 'Canucks',
    	'result_type': 'recent',
    	'count': 2
	}

	search_url = '{}1.1/search/tweets.json'.format(base_url)
	search_resp = requests.get(search_url, headers=search_headers, params=search_params)
	tweet_data = search_resp.json()
	
	for x in tweet_data['statuses']:
	    print(x['text'] + '\n')

get_canuck_tweets()
