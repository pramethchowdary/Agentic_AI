from flask import Flask, request,render_template
import tweet_extractor as twitter
import pipeline as agent

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("landing.html")

@app.route('/extract', methods=['POST'])
def extract():
    if request.method == 'POST':
        url = request.form['tweet_url']
        if not url:
            return "Tweet URL is required.", 400
        tweet_id = url.rstrip("/").split("/")[-1]
        tweet = twitter.extract_tweet_info(tweet_id)
        verdict = agent.main_brain_agent(tweet['text'], tweet['username'])

        return render_template("details.html", tweet=tweet, verdict=verdict)
    return "Invalid Request", 400


if __name__ == "__main__":
    app.run(port=5000)   # Run on port 5000