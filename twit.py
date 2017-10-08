import tweepy
from tweepy.streaming import StreamListener
from tweepy import Stream
from local_config import *
import json
from collections import Counter

swear_words = ["idiot", "hate", "horrible", "terrible", "stupid", "disgrace", "awful", "worst", "lie", "bad"]
love_words = ["love", "thank", "happy", "bless", "wonderful", "amazing", "perfect", "great", "best"]

langs = {'ar': 'Arabic', 'bg': 'Bulgarian', 'ca': 'Catalan', 'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish', 'et': 'Estonian',
         'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'iw': 'Hebrew',
         'ja': 'Japanese', 'ko': 'Korean', 'lt': 'Lithuanian', 'lv': 'Latvian', 'ms': 'Malay', 'nl': 'Dutch', 'no': 'Norwegian', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian',
         'ru': 'Russian', 'sk': 'Slovak', 'sl': 'Slovenian', 'sr': 'Serbian', 'sv': 'Swedish', 'th': 'Thai', 'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu',
         'vi': 'Vietnamese', 'zh_CN': 'Chinese (simplified)', 'zh_TW': 'Chinese (traditional)'}

countries = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina', 'Burundi', 'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', '"Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe', 'Afghanistan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Burma (Myanmar)', 'Cambodia', 'China', 'East Timor', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', '"Korea', '"Korea', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia', 'Nepal', 'Oman', 'Pakistan', 'Philippines', 'Qatar', 'Russian Federation', 'Saudi Arabia', 'Singapore', 'Sri Lanka', 'Syria', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen', 'Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macedonia', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom', 'Vatican City', 'Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Canada', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'El Salvador', 'Grenada', 'Guatemala', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'United States', 'Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu', 'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela']


class twitter_listener(StreamListener):

    def __init__(self, num_tweets_to_grab, stats, retweet_count=1000):
        self.counter = 0
        self.num_tweets_to_grab = num_tweets_to_grab
        self.retweet_count = retweet_count
        self.stats = stats

    def on_data(self, data):
        try:
            json_data = json.loads(data)
            tweet = json_data["text"]
            location = json_data["user"]["location"]

            if "," in location:
                location = location.split(",")[1].strip()

            self.stats.add_lang(langs[json_data["lang"]])

            for l in love_words:
                if l in tweet.lower():
                    self.stats.add_love()

            for l in swear_words:
                if l in tweet.lower():
                    self.stats.add_hate()

            for c in countries:
                if c in location:
                    self.stats.add_country(c)

            if "USA" in location:
                self.stats.add_country("United States")

            self.counter += 1
            retweet_count = json_data["retweeted_status"]["retweet_count"]

            if retweet_count >= self.retweet_count:
                self.stats.add_top_tweets(json_data["text"])

            if self.counter >= self.num_tweets_to_grab:
                return False
            return True
        except:
            pass

    def on_error(self, status):
        print("")

class TwitterMain():
    def __init__(self, num_tweets_to_grab, retweet_count):
        self.auth = tweepy.OAuthHandler(cons_tok, cons_sec)
        self.auth.set_access_token(app_tok, app_sec)
        self.api = tweepy.API(self.auth)
        self.num_tweets_to_grab = num_tweets_to_grab
        self.retweet_count = retweet_count
        self.stats = stats()

    def get_streaming_data(self):
        twitter_stream = Stream(self.auth, twitter_listener(num_tweets_to_grab=self.num_tweets_to_grab, retweet_count = self.retweet_count, stats = self.stats))
        try:
            twitter_stream.filter(track=[query]).sample()
        except Exception as e:
            print("")

        lang, top_tweets, pos, neg, countries = self.stats.get_stats()
        print("These are the languages that people that are talking about " + query + " are using.")
        print(Counter(lang))
        print("")
        print("These are the languages that people that are talking about " + query + " are tweeting from.")
        print(Counter(countries))
        print("")
        print("The tweets for " + query + "  are " + str(pos) + "% Positive")
        print("The tweets for " + query + "  are " + str(neg) + "% Negative")
        print("")
        print("Here are some of the top tweets for " + query)
        for i in range(3):
            print top_tweets[i]


class stats():

    def __init__(self):
        self.lang = []
        self.top_tweets = []
        self.love = 1.0
        self.hate = 1.0
        self.pos = 0
        self.neg = 0
        self.countries = []

    def add_lang(self, lang):
        self.lang.append(lang)

    def add_top_tweets(self, tweet):
        self.top_tweets.append(tweet)

    def add_love(self):
        self.love += 1

    def add_hate(self):
        self.hate += 1

    def add_country(self, country):
        self.countries.append(country)

    def get_stats(self):
        self.pos = int(self.love/(self.hate + self.love) * 100)
        self.neg = int(100 - self.pos)
        return self.lang, self.top_tweets, self.pos, self.neg, self.countries


if __name__ == "__main__":
    num_tweets_to_grab = 100
    retweet_count = 10000
    query = raw_input("Please enter something: ")
    print("Searching for " +  query)
    print("----------------------------------------------")
    twit = TwitterMain(num_tweets_to_grab, retweet_count)
    twit.get_streaming_data()
