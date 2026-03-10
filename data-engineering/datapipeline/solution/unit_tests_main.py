import pytest
import json
import pandas as pd
from main import get_data, process_date_time, from_seconds_to_original_fastest_lap_time, from_fastest_lap_time_to_seconds, get_race_winner, get_fastest_lap_time, prepare_output, export_as_json_per_year    

RACES_PATH = '../source_data/races.csv'
RESULTS_PATH = '../source_data/results.csv'
RESULTS_OUTPUT_PATH = '../results/'

def test_get_data():
    data = get_data(RACES_PATH, RESULTS_PATH)
    assert not data.empty, "The resulting df should not be empty"


def test_from_fastest_lap_time_to_seconds():
    assert from_fastest_lap_time_to_seconds("1:30.0") == 90, "Should convert 1:30.0 to 90 seconds"
    assert from_fastest_lap_time_to_seconds("01:43.0") == 103, "Should convert 1:43.0 to 103 seconds"


def test_from_seconds_to_original_fastest_lap_time():
    assert from_seconds_to_original_fastest_lap_time(90) == "1:30.0", "Should convert 90 seconds to 1:30.0"
    assert from_seconds_to_original_fastest_lap_time(103) == "1:43.0", "Should convert 103 seconds to 1:43.0"


def test_process_date_time():
    df = pd.DataFrame({
        'date': ['2019-12-01', '2019-06-23'],
        'time': ['13:10:00.000', '13:10:00.000']
    })
    res_df = process_date_time(df)
    assert 'datetime' in res_df.columns, "It should create the new concatenated column as 'datetime'"


def test_get_race_winner():
    df = pd.DataFrame({
        'raceId': [1, 2, 2, 3, 4],
        'driverId': ['id1', 'id2', 'id3', 'id4', 'id5'],
        'position': [1.0, 3.0, 2.0, 4.0, 1.0]
    })
    winner = get_race_winner(df)
    assert winner['Race Winning driverId'][0] == 'id1', "The driver with 'id1' should be the winner of race 1"
    assert winner['Race Winning driverId'][4] == 'id5', "The driver with 'id5' should be the winner of race 4"

def test_get_fastest_lap_time():
    df = pd.DataFrame({             
        'raceId': [2, 2, 4, 3, 2],
        'driverId': ['id1', 'id2', 'id3', 'id4', 'id5'],
        'fastestLapTime': ['1:30.4', '1:43.9', '1:35.3', '1:50.0', '1:25.0']
    })
    fastest_lap_time = get_fastest_lap_time(df)
    assert fastest_lap_time[fastest_lap_time['raceId'] == 2]['Race Fastest Lap'].iloc[0] == '1:25.0', "The fastest lap is 1:25.0"


def test_prepare_output():
    data = get_data(RACES_PATH, RESULTS_PATH)
    output = prepare_output(data)
    assert len(output) > 0, "The Json-ready data should not be empty"


def test_export_as_json_per_year():
    data = get_data(RACES_PATH, RESULTS_PATH)
    json_output = prepare_output(data)
    export_as_json_per_year(json_output, RESULTS_OUTPUT_PATH )
    with open('../results/stats_2018.json', 'r') as f:
        json_data = json.load(f)
        assert "Abu Dhabi Grand Prix" in json_data[0]['Race Name'], "The Abu Dhabi Grand Prix should be in the 2018 races"