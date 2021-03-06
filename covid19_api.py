#!/usr/bin/env python3
'''
    covid19_api.py
    author: Claire Schregardus
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
    '''Returns a dictionery of state abbreviations and state ids'''
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
    '''Returns the corresponding state abbreviation given a state id'''
    abbreviations_dict = get_abbreviations_dict()
    state_abbreviation = abbreviations_dict[state_id]
    return state_abbreviation

def get_cumulative_dictionary(state_abbreviation):
    '''Returns a dictionary with cumulative information about a given state'''
    try:
        cursor = connection.cursor()
        query = 'SELECT date, state_id, new_deaths, new_positive_tests, new_negative_tests, new_hospitalizations FROM covid19_days'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()
    state_cumulative_info = {}
    state_list = []
    date_list = []
    deaths = 0
    positive_tests = 0
    negative_tests = 0
    hospitalizations = 0
    for row in cursor:
        state = get_state_abbreviation(row[1])
        if state.startswith(state_abbreviation):
            if state in state_list:
                deaths += row[2]
                positive_tests += row[3]
                negative_tests += row[4]
                hospitalizations += row[5]
                date_list.append(row[0])
            else:
                deaths = row[2]
                positive_tests = row[3]
                negative_tests = row[4]
                hospitalizations = row[5]
                state_list.append(state)
                date_list.append(row[0])
    start_date = str(date_list[-1])
    end_date = str(date_list[0])
    state_cumulative_info = {'start_date': start_date, 'end_date': end_date, 'state': state_abbreviation, 'deaths': deaths, \
        'positive_tests': positive_tests, 'negative_tests': negative_tests, 'hospitalizations': hospitalizations}
    return state_cumulative_info

@app.route('/state/<state_abbreviation>/daily')
def get_state(state_abbreviation):
    ''' Returns a list of dictionaries, each representing the COVID-19 statistics from the specified state on a single date. 
        Each dictionary will have the following fields:
        date -- YYYY-MM-DD (e.g. "2020-10-08")
        state -- upper-case two-letter state abbreviation (e.g. "MN")
        deaths -- (integer) the number of deaths on this date
        positive -- (integer) the number of positive COVID-19 tests on this date
        negative -- (integer) the number of negative COVID-19 tests on this date
        hospitalizations -- (integer) the number of new hospitalizations for COVID-19 on this date'''
    try:
        cursor = connection.cursor()
        query = 'SELECT date, state_id, new_deaths, new_positive_tests, new_negative_tests, new_hospitalizations FROM covid19_days'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()
    state_info = {}
    state_info_list = []
    for row in cursor:
        state = get_state_abbreviation(row[1])
        if state.startswith(state_abbreviation):
            state_info = {'date': str(row[0]), 'state': state, 'deaths': str(row[2]), 'positive_tests': str(row[3]),
            'negative_tests': str(row[4]), 'hospitalizations': str(row[5])}
            state_info_list.append(state_info)
    return json.dumps(state_info_list)

@app.route('/state/<state_abbreviation>/cumulative')
def get_state_cumulative(state_abbreviation):
    '''Returns a single dictionary representing the cumulative statistics for the specified state. 
       Each dictionary will have the following fields:
       start_date -- YYYY-MM-DD (e.g. "2020-10-08")
       end_date -- YYYY-MM-DD (e.g. "2020-03-11")
       state -- upper-case two-letter state abbreviation (e.g. "MN")
       deaths -- (integer) the total number of deaths between the start and end dates (inclusive)
       positive -- (integer) the number of positive COVID-19 tests between the start and end dates (inclusive)
       negative -- (integer) the number of negative COVID-19 tests between the start and end dates (inclusive)
       hospitalizations -- (integer) the number of hospitalizations between the start and end dates (inclusive)'''
    state_cumulative_info = get_cumulative_dictionary(state_abbreviation)
    return json.dumps(state_cumulative_info)
  

@app.route('/states/cumulative')
def get_all_states_cumulative():
    '''Returns a list of dictionaries each representing the cumulative COVID-19 statistics for each state. 
    The dictionaries are sorted in decreasing order of deaths, cases (i.e. positive tests), or hospitalizations,
    depending on the value of the GET parameter "sort". If sort is not present, then the list will be sorted by deaths.
    Each dictionary will have the following fields:
    start_date -- YYYY-MM-DD (e.g. "2020-10-08")
    end_date -- YYYY-MM-DD (e.g. "2020-03-11")
    state -- upper-case two-letter state abbreviation (e.g. "MN")
    deaths -- (integer) the total number of deaths between the start and end dates (inclusive)
    positive -- (integer) the number of positive COVID-19 tests between the start and end dates (inclusive)
    negative -- (integer) the number of negative COVID-19 tests between the start and end dates (inclusive)
    hospitalizations -- (integer) the number of hospitalizations between the start and end dates (inclusive)'''
    try:
        cursor = connection.cursor()
        query = 'SELECT abbreviation FROM states'
        cursor.execute(query)
    except Exception as e:
        print(e)
        exit()
    state_list = []
    state_dict_list = []
    for row in cursor:
        state_list.append(row[0])
    for state in state_list:
        state_cumulative_info = get_cumulative_dictionary(state)
        state_dict_list.append(state_cumulative_info)

    if flask.request.args.get('sort') == 'deaths':
        states_deaths_sort = sorted(state_dict_list, key=lambda k: k['deaths'], reverse=True) 
        return json.dumps(states_deaths_sort)
    elif flask.request.args.get('sort') == 'cases':
        states_cases_sort = sorted(state_dict_list, key=lambda k: k['positive_cases'], reverse=True) 
        return json.dumps(states_cases_sort)
    elif flask.request.args.get('sort') == 'hospitalizations':
        states_hospitalizations_sort = sorted(state_dict_list, key=lambda k: k['hospitalizations'], reverse=True) 
        return json.dumps(states_hospitalizations_sort)
    else:
        states_deaths_sort = sorted(state_dict_list, key=lambda k: k['deaths'], reverse=True) 
        return json.dumps(states_deaths_sort)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('A sample Flask application/API')
    parser.add_argument('host', help='the host on which this application is running')
    parser.add_argument('port', type=int, help='the port on which this application is listening')
    arguments = parser.parse_args()
    app.run(host=arguments.host, port=arguments.port, debug=True)