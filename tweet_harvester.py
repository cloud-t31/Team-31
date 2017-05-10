import couchdb
import tweepy
from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from http.client import IncompleteRead
from requests.packages.urllib3.exceptions import ProtocolError
import time
import json
import sys
from process_tweet import get_sentiment

s = 0

server1 = {

    'credentials': {
        'ckey': "OHI0JxEJTCQkxkT33UPV9uUGp",
        'csecret': "js0t06Ygmo2BNCBEikIxqL0WZo2xx3QK2oDkYF7HnMzb43vrWF",
        'atoken': "1905695318-EDgCqaTRFdiphMIk8zhPZdCBGv1mTYRAsNRp8mT",
        'asecret': "DyWioMKeZkrdRdhDllGiSWd8h5ptPuTCPLt8XRxOjhHra"
    },
    'coords': [144.402136, -38.086704, 144.869945, -37.466856]  # left melb
}

server2 = {

    'credentials': {
        'ckey': "i7ncX1Fd9rMAjhiHTDKECdkw2",
        'csecret': "SaPwhBV0NV6Tbt4F4g3c4MAOMAE9poUbvq380hk3YWKX2g90xO",
        'atoken': "1905695318-FVIdHzBbEasp7GFme0NcR5cvGRsPX2mLEfS1fy9",
        'asecret': "59Pq78wl4i4sPud2QaSgO4CIcoIPeo9Jt0UQjUsnifpyM"
    },
    'coords': [144.786911, -37.947082, 145.050327, -37.466856]  # center melb
}

server3 = {
    'credentials': {
        'ckey': "h5gu8FLrUIhDkf1EQRlPG489r",
        'csecret': "l7WMHYgFixacodtjrMHTmPRf6gmMCDhPAETJD5Q6pE3qS3NtpD",
        'atoken': "1905695318-BCEcjLybmkHFhHiOSMp9vwciLfzX3BXC7jcm1LL",
        'asecret': "Csad6IWjAOKMbk5BYxwCFi6JjHaKVHtASEzw03dMHO2aw"
    },
    'coords': [144.975884, -38.208528, 145.760405, -37.480490]  # right melb
}

servers = [
    server1,
    server2,
    server3
]

server = servers[s]

db_name = 'test_db'

couch = couchdb.Server('http://146.118.102.201:5984')
couch.resource.credentials = ('admin', 'admin')
db = couch[db_name]


class MyListener(StreamListener):
    def on_data(self, raw_data):
        json_data = json.loads(raw_data)
        json_data["_id"] = json_data["id_str"]
        json_data['type'] = 'tweet'
        json_data["sentiment"] = get_sentiment(json_data["text"])
        while True:
            try:
                db.save(json_data)
                break
            except couchdb.http.ResourceConflict:
                break
            except couchdb.http.ServerError as e:
                print("Server error %s. Sleeping for 60 seconds" % e)
                sys.stdout.flush()
                time.sleep(60)
        return True

    def on_error(self, status):
        print("Error: " + str(status))
        sys.stdout.flush()


auth = OAuthHandler(server['credentials']['ckey'], server['credentials']['csecret'])
auth.set_access_token(server['credentials']['atoken'], server['credentials']['asecret'])

print("start")
sys.stdout.flush()

while True:

    try:
        twitterStream = Stream(auth, MyListener())
        twitterStream.filter(locations=server['coords'], languages=['en'])
    except (IncompleteRead, ProtocolError, AttributeError):
        print("Twitter Error: Sleeping for 5 seconds")
        sys.stdout.flush()
        time.sleep(5)
        continue
    except KeyboardInterrupt:
        twitterStream.disconnect()
        break
    except Exception as e:
        print("Unknown Error %s: Sleeping for 10 seconds - " % e)
        sys.stdout.flush()
        time.sleep(10)
    except tweepy.error.RateLimitError:
        print(" Rate limit error: sleeping for 1000 seconds")
        sys.stdout.flush()
        time.sleep(1000)
    sys.stdout.flush()
