import slack
import os
import json
import requests
import random
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import gspread
from oauth2client.service_account import ServiceAccountCredentials

new_line = "\n"

# sets environmental variable file path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# creates Flask App and SlackEventAdapter API with bot key
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

# sets slack token
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

# get movie list from sheets
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

clientg = gspread.authorize(creds)

sheet = clientg.open("Filmclub_List").sheet1

movie_list = sheet.col_values(2)
date_list = sheet.col_values(1)

# make movie dictionary Key: Title Value: Date Watched
movie_dict = {movie_list[i]: date_list[i] for i in range(len(movie_list))}

# make not watched movie list by searching for null date values in movie list dictionary
notwatched_movie_list = [key  for (key, value) in movie_dict.items() if value == 'null']

# list of commands
commands = ["QUID VIGILE", "veto", "TRUMP", "unum de eis"]





# Shitty API poster get. Only works if Movie Title is in correct case. Might not work if date is included
def get_poster(movie_title):
  CONFIG_PATTERN = 'http://www.omdbapi.com/?apikey={key}&s={title_search}'
  KEY = '6209ccda'
  title_search = movie_title
  url = CONFIG_PATTERN.format(key=KEY, title_search=title_search)
  r = requests.get(url)
  search_return = r.json()
  if search_return.get('Response') == 'False':
    return('NO POSTER!')
  else:
    search_return_list = search_return.get('Search')
    first_search_dic = (next((item for item in search_return_list if item["Title"] == title_search), None))
    if first_search_dic != 'None':
      poster_url = str(first_search_dic.get('Poster'))
      poster_url600 = str(poster_url.replace("300", "600"))
      just_watch_link = ('https://www.justwatch.com/us/search?q=' + movie_title).replace(" ", "-")
      poster_link = poster_url600 + new_line + just_watch_link  
      print(just_watch_link)
      return(poster_link)

# message trigger read and parse
@slack_event_adapter.on('message')
def message(payload):
	event = payload.get('event', {})
	channel_id = event.get('channel')
	user_id = event.get('user')
	text = event.get('text')

	if BOT_ID != user_id:
		if text == 'QUID VIGILE':
			random_movie = random.choice(notwatched_movie_list)
			poster_url = get_poster(random_movie)
			movie_text = random_movie + '\n' + poster_url
			client.chat_postMessage(channel=channel_id, text=movie_text)
		elif text == 'unum de eis':
			film_club = ['Andy', 'Alex', 'Ilya', 'Matt', 'Seth', 'Paul', 'Jeremy', 'Richard', 'Kyle']
			film_club_random = random.sample(film_club, 9)
			new_line = "\n"
			film_club_random_list = new_line.join(film_club_random)
			client.chat_postMessage(channel=channel_id, text=film_club_random_list)
		elif text == 'TRUMP':
			#trump_file = {'file' : ('C:\\Python_Scripts\\Theodosius_SlackAPP\\trump.gif', open('C:\\Python_Scripts\\Theodosius_SlackAPP\\trump.gif', 'rb'), 'gif')}
			#payload_file={"filename":"trump.gif", "token":os.environ['SLACK_TOKEN'], "channels":['#test']}
			#r = requests.post("https://slack.com/api/files.upload", params=payload_file, files=trump_file)
			client.chat_postMessage(channel=channel_id, text = "https://media.giphy.com/media/jSB2l4zJ82Rvq/giphy.gif")
			
		

# main Flask app
if __name__ == "__main__":
	app.run(debug=True)