#!/usr/bin/env python3
'''
    covid19_api.py

    16 October 2020
'''
import sys
import argparse
import flask
import json
import psycopg2

app = flask.Flask(__name__)

try:
    connection = psycopg2.connect(database = 'covid19')
except Exception as e:
    print(e)
    exit()

def get_abbreviations_dict():
    try:
        cursor = connection.cursor()
        query = 'SELECT abbreviation, id FROM states'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()
    abbreviations_dict = {}
    for row in cursor:
        abbreviation = row[0]
        id_num = row[1]
        abbreviations_dict[id_num] = abbreviation
    return abbreviations_dict

def get_state_abbreviation(state_id):
    abbreviations_dict = get_abbreviations_dict()
    state_abbreviation = abbreviations_dict[state_id]
    return state_abbreviation

@app.route('/state/<state_abbreviation>/daily')
def get_state(state_abbreviation):
    ''' Returns a list of dictionaries, each representing the COVID-19 statistics from the specified state on a single date. 
        date -- YYYY-MM-DD (e.g. "2020-10-08")
        state -- upper-case two-letter state abbreviation (e.g. "MN")
        deaths -- (integer) the number of deaths on this date
        positive -- (integer) the number of positive COVID-19 tests on this date
        negative -- (integer) the number of negative COVID-19 tests on this date
        hospitalizations -- (integer) the number of new hospitalizations for COVID-19 on this date'''
    try:
        cursor = connection.cursor()
        query = 'SELECT date, state_id, deaths, new_positive_tests, new_negative_tests, new_hospitalizations FROM covid19_days'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()
    state_info = {}
    state_info_list = []
    for row in cursor:
        if get_state_abbreviation(row[1]).startswith(state_abbreviation):
            state_info = {'date': str(row[0]), 'state': get_state_abbreviation(row[1]), 'deaths': str(row[2]), 'new_positive_tests': str(row[3]),
            'new_negative_tests': str(row[4]), 'new_hospitalizations': str(row[5])}
            state_info_list.append(state_info)
    return json.dumps(state_info_list)

@app.route('/state/<state_abbreviation>/cumulative')
def get_state_cumulative(state_abbreviation):
    '''Returns a single dictionary representing the cumulative statistics for the specified state.
       start_date -- YYYY-MM-DD (e.g. "2020-10-08")
       end_date -- YYYY-MM-DD (e.g. "2020-03-11")
       state -- upper-case two-letter state abbreviation (e.g. "MN")
       deaths -- (integer) the total number of deaths between the start and end dates (inclusive)
       positive -- (integer) the number of positive COVID-19 tests between the start and end dates (inclusive)
       negative -- (integer) the number of negative COVID-19 tests between the start and end dates (inclusive)
       hospitalizations -- (integer) the number of hospitalizations between the start and end dates (inclusive)'''
    try:
        cursor = connection.cursor()
        query = 'SELECT date, state_id, deaths, new_positive_tests, new_negative_tests, new_hospitalizations FROM covid19_days'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()
    state_cumulative_info = {}
    deaths = 0
    positive_tests = 0
    negative_tests = 0
    hospitalizations = 0
    for row in cursor:
       # new_deaths = row[2]
        if get_state_abbreviation(row[1]).startswith(state_abbreviation):
            deaths += row[2]
            positive_tests += row[3]
            negative_tests += row[4]
            hospitalizations += row[5]
         #   if get_state_abbreviation(row[1]) in state_cumulative_info:
          #      state_cumulative_info = {}
    state_cumulative_info = {'start_date': str(row[0]), 'end_date': str(row[0]), 'state': get_state_abbreviation(row[1]), 'deaths': deaths, \
        'new_positive_tests': positive_tests, 'new_negative_tests': negative_tests, 'new_hospitalizations': hospitalizations}
    return json.dumps(state_cumulative_info)
    #how to get start_date and end_date??
    #also how to get cumulatiive?

@app.route('/states/cumulative')
def get_all_states():
    '''Returns a list of dictionaries each representing the cumulative COVID-19 statistics for each state. 
    The dictionaries are sorted in decreasing order of deaths, cases (i.e. positive tests), or hospitalizations,
    depending on the value of the GET parameter "sort". If sort is not present, then the list will be sorted by deaths.
    start_date -- YYYY-MM-DD (e.g. "2020-10-08")
    end_date -- YYYY-MM-DD (e.g. "2020-03-11")
    state -- upper-case two-letter state abbreviation (e.g. "MN")
    deaths -- (integer) the total number of deaths between the start and end dates (inclusive)
    positive -- (integer) the number of positive COVID-19 tests between the start and end dates (inclusive)
    negative -- (integer) the number of negative COVID-19 tests between the start and end dates (inclusive)
    hospitalizations -- (integer) the number of hospitalizations between the start and end dates (inclusive)'''
    deaths = flask.request.args.get('deaths')
    cases = flask.request.args.get('cases')
    hopsitalizations = flask.request.args.get('hospitalizations')
    try:
        cursor = connection.cursor()
        query = 'SELECT date, state_id, deaths, new_positive_tests, new_negative_tests, new_hospitalizations FROM covid19_days'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()

    state_info = {}
    for row in cursor:
        state_info = {'date': str(row[0]), 'state': get_state_abbreviation(row[1]), 'deaths': str(row[2]), 'new_positive_tests': str(row[3]),
        'new_negative_tests': str(row[4]), 'new_hospitalizations': str(row[5])}
  
    return json.dumps(state_info)
    #sorting??

if __name__ == '__main__':
    parser = argparse.ArgumentParser('A sample Flask application/API')
    parser.add_argument('host', help='the host on which this application is running')
    parser.add_argument('port', type=int, help='the port on which this application is listening')
    arguments = parser.parse_args()
    app.run(host=arguments.host, port=arguments.port, debug=True)