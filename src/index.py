from flask import Flask, request
import HowsTheMovie
import json

app = Flask (__name__)

@app.route('/',methods=['GET'])
def index():
	response = {}
	response["Status"] = "Success"
	return json.dumps(response)

@app.route('/howsthemovie/getmoviedetails', methods = ['GET'])
def get_movie_details():
	movie_name = request.args.get('movie_name') 
	if movie_name is not None or movie_name: 
		return json.dumps(HowsTheMovie.get_movie_details(movie_name)) , 200
	return 'Movie Name is a required parameter for this call', 400

@app.route('/howsthemovie/gettwittersentiments', methods=['GET'])
def get_twitter_sentiments():
	hashtag = request.args.get('hashtag') 
	if hashtag is not None or hashtag: 
		return json.dumps(HowsTheMovie.get_twitter_sentiments(hashtag.strip().replace(' ',''))), 200
	return 'Hashtag is a required parameter for this call', 400

@app.errorhandler(404)
def page_not_found(e):
	return 'oh! Something is not right. :('