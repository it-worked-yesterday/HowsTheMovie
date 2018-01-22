# HowsTheMovie
Scrapes movie/TV Series details from IMDB and analyses twitter sentiments about the same. 

- Front end src : https://github.com/it-worked-yesterday/HowsTheMovie-FrontEnd
- Website : http://howsthemovie.pytch.in 

This module creates 2 rest apis based on Python/Flask open for `GET` requests:
1. getmoviedetails : Scrapes information from IMDB about a movie/TV series. Returns movie object or None if nothing is found.
2. gettwittersentiments : Fetches tweets with the above movie/TV series title in hashtag and analyses the sentiments. (Pos/Neg/Neutal)

## Getting Twitter access tokens
- Login to [apps.twitter.com](https://apps.twitter.com)  with your twitter credentials 
- Create a new twitter app
- Generate access tokens
Refer to [twitter's page](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens) for more. 

## Running locally (with Python3)

Clone the repo
```
$ git clone https://github.com/it-worked-yesterday/HowsTheMovie-FrontEnd.git
```

Now create the virtualenv of Python3.6 using
```
$ conda create --name howsTheMovie python=3
```

Activate the environment and install requirements using pip, navigate to linkedin folder which have spider as a subfolder and start the bot
```
$ source activate howsTheMovie
$ pip install -r requirements.txt
```

**Set Consumer and Access keys** 
- open confg/config.ini
- replace the consumer and access keys with ones generated at [apps.twitter.com](https://apps.twitter.com)


**Run the flask app**
```
$ export FLASK_APP=index.py
$ export FLASK_DEBUG=1
$ python -m flask run
```

The flask server will create 2 Rest endpoints locally, which you can : 
1. `0.0.0.0:5000/howsthemovie/getmoviedetails?movie_name=`
2. `0.0.0.0:5000/howsthemovie/gettwittersentiments?hashtag=`


> __NOTE__
> When hosting to a server be sure to add `app.run(host=<host>, port=<port>)` to index.py file as per the hosting service 
> documentation.
