#!/usr/bin/env python3
'''
    flask_sample.py
    Jeff Ondich, 22 April 2016
    Updated 7 October 2020
    A slightly more complicated Flask sample app than the
    "hello world" app found at http://flask.pocoo.org/.
'''
import sys
import argparse
import flask
import json

app = flask.Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Citizen of CS257.'

@app.route('/actor/<last_name>')
def get_actor(last_name):
    ''' Returns the first matching actor, or an empty dictionary if there's no match. '''
    actor_dictionary = {}
    lower_last_name = last_name.lower()
    for actor in actors:
        if actor['last_name'].lower().startswith(lower_last_name):
            actor_dictionary = actor
            break
    return json.dumps(actor_dictionary)

@app.route('/movies')
def get_movies():
    ''' Returns the list of movies that match GET parameters:
          start_year, int: reject any movie released earlier than this year
          end_year, int: reject any movie released later than this year
          genre: reject any movie whose genre does not match this genre exactly
        If a GET parameter is absent, then any movie is treated as though
        it meets the corresponding constraint. (That is, accept a movie unless
        it is explicitly rejected by a GET parameter.)
    '''
    movie_list = []
    genre = flask.request.args.get('genre')
    start_year = flask.request.args.get('start_year', default=0, type=int)
    end_year = flask.request.args.get('end_year', default=10000, type=int)
    for movie in movies:
        if genre is not None and genre != movie['genre']:
            continue
        if movie['year'] < start_year:
            continue
        if movie['year'] > end_year:
            continue
        movie_list.append(movie)

    return json.dumps(movie_list)

@app.route('/help')
def get_help():
    help_message = ''
    with flask.current_app.open_resource('static/help.html', 'r') as f:
        help_message = f.read()
    return help_message

if __name__ == '__main__':
    parser = argparse.ArgumentParser('A sample Flask application/API')
    parser.add_argument('host', help='the host on which this application is running')
    parser.add_argument('port', type=int, help='the port on which this application is listening')
    arguments = parser.parse_args()
    app.run(host=arguments.host, port=arguments.port, debug=True)