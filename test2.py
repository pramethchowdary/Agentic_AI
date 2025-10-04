# this example uses requests
import requests
import json
import os
import dotenv
dotenv.load_dotenv()

params = {
  'url': 'https://sightengine.com/assets/img/examples/example-prop-c1.jpg',
  'models': 'genai',
  'api_user': os.getenv("API_USER"),
  'api_secret': os.getenv("API_SECRET")
}
r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)

output = json.loads(r.text)