import tweepy
import os
from dotenv import load_dotenv

load_dotenv()
bearer_token = os.environ.get("token")

if bearer_token:
    client = tweepy.Client(bearer_token=bearer_token)
else:
    client = None

def extract_tweet_info(tweet_id) -> dict:
    if not client:
        raise Exception("Bearer token not found. Please check your .env file.")
    try:
        tweet = client.get_tweet(
            id=tweet_id,
            expansions=["attachments.media_keys", "author_id"],
            tweet_fields=["created_at", "public_metrics", "text"],
            media_fields=["url", "preview_image_url", "type"],
            user_fields=["username", "name", "profile_image_url"]
        )
        list_data = {}
        list_data['text'] = tweet.data.text
        list_data['username'] = tweet.includes['users'][0].username
        list_data['name'] = tweet.includes['users'][0].name
        list_data['profile_image_url'] = tweet.includes['users'][0].profile_image_url
        list_data['created_at'] = tweet.data.created_at
        metrics = tweet.data.public_metrics 
        list_data['likes'] = metrics['like_count']
        list_data['retweets'] = metrics['retweet_count']
        list_data['replies'] = metrics['reply_count']
        if "media" in tweet.includes:
            media_urls = []
            for media in tweet.includes['media']:
                media_type = media.type
                media_url = getattr(media, "url", getattr(media, "preview_image_url", None))
                media_urls.append({'type': media_type, 'url': media_url})
            list_data['media'] = media_urls
        return list_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    