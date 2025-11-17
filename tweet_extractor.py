import tweepy

def create_twitter_client(bearer_token: str):
    """
    Create a Tweepy client using the provided bearer token.
    """
    if not bearer_token:
        raise ValueError("Bearer token is missing. Please provide a valid token.")
    return tweepy.Client(bearer_token=bearer_token)


def extract_tweet_info(tweet_id: str, bearer_token: str) -> dict:
    """
    Extracts tweet information using the provided bearer token.
    """
    try:
        client = create_twitter_client(bearer_token)

        tweet = client.get_tweet(
            id=tweet_id,
            expansions=["attachments.media_keys", "author_id"],
            tweet_fields=["created_at", "public_metrics", "text"],
            media_fields=["url", "preview_image_url", "type"],
            user_fields=["username", "name", "profile_image_url"]
        )

        list_data = {
            'text': tweet.data.text,
            'username': tweet.includes['users'][0].username,
            'name': tweet.includes['users'][0].name,
            'profile_image_url': tweet.includes['users'][0].profile_image_url,
            'created_at': tweet.data.created_at,
        }

        metrics = tweet.data.public_metrics
        list_data.update({
            'likes': metrics['like_count'],
            'retweets': metrics['retweet_count'],
            'replies': metrics['reply_count']
        })

        # Handle media if present
        if "media" in tweet.includes:
            media_urls = [
                {
                    'type': media.type,
                    'url': getattr(media, "url", getattr(media, "preview_image_url", None))
                }
                for media in tweet.includes['media']
            ]
            list_data['media'] = media_urls

        return list_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
