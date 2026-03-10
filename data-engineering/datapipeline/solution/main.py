import pandas as pd
import json

RACES_PATH = '../source-data/races.csv'
RESULTS_PATH = '../source-data/results.csv'
RESULTS_OUTPUT_PATH = '../results/'

def get_data(races_path, results_path):
    races = pd.read_csv(races_path)
    results = pd.read_csv(results_path)
    # can have more results for one single race --> parent (races) - child (results)
    joined_df = races.merge(results, on='raceId', how='left')
    duplicates_check = joined_df[joined_df.duplicated(subset=['raceId', 'driverId'], keep=False)]
    assert duplicates_check.empty, 'There are duplicates in the joined df'
    return joined_df


def process_date_time(joined_df):
    joined_df['time'] = joined_df['time'].fillna('00:00:00')
    joined_df['datetime'] = pd.to_datetime(joined_df['date'] + ' ' + joined_df['time'])
    joined_df['datetime'] = joined_df['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S.000') 
    return joined_df


def get_race_winner(joined_df):
    winner_driver = joined_df[joined_df['position'] == 1.0][['raceId', 'driverId']] 
    winner_driver = winner_driver.rename(columns={'driverId': "Race Winning driverId"})
    return winner_driver


def from_fastest_lap_time_to_seconds(fastest_lap_time):
    if pd.isna(fastest_lap_time):
        return None
    minutes, seconds = fastest_lap_time.split(':')
    total_in_seconds = float(minutes) * 60 + float(seconds)
    
    return total_in_seconds


def from_seconds_to_original_fastest_lap_time(fastest_lap_time):
    if pd.isna(fastest_lap_time):
        return None
    minutes = fastest_lap_time // 60
    seconds = fastest_lap_time % 60
    return f'{int(minutes)}:{seconds:.1f}'


def get_fastest_lap_time(joined_df):
    # convert the lap time to seconds to get the smallest value
    joined_df['fastestLapTime'] = joined_df['fastestLapTime'].apply(from_fastest_lap_time_to_seconds)
    fastest_lap_per_race = joined_df.groupby('raceId')['fastestLapTime'].min().reset_index()
    fastest_lap_per_race = fastest_lap_per_race[['raceId', 'fastestLapTime']]
    fastest_lap_per_race = fastest_lap_per_race.rename(columns={'fastestLapTime': 'Race Fastest Lap'})

    # convert the lap time back to the original format
    fastest_lap_per_race['Race Fastest Lap'] = fastest_lap_per_race['Race Fastest Lap'].apply(from_seconds_to_original_fastest_lap_time)
    return fastest_lap_per_race


def prepare_output(joined_df):
    joined_df =process_date_time(joined_df)
    winner_driver = get_race_winner(joined_df)
    fastest_lap_per_race = get_fastest_lap_time(joined_df)
    race_analytics_output = joined_df.merge(winner_driver, on='raceId', how='left') 
    race_analytics_output = race_analytics_output.merge(fastest_lap_per_race, on='raceId', how='left') 

    race_analytics_cols_to_keep = race_analytics_output[[
                                'name', 
                                'year',
                                'round',
                                'datetime',
                                'Race Winning driverId',
                                'Race Fastest Lap']
                            ].rename(columns={
                                'name': 'Race Name', 
                                'round': 'Race Round',
                                'datetime': 'Race Datetime',
                            })

    # "The json value for a key is always a number, represent it as such rather than a string"
    race_analytics_cols_to_keep[race_analytics_cols_to_keep['Race Winning driverId'].isna()] = None
    race_analytics_cols_to_keep['Race Winning driverId'] = race_analytics_cols_to_keep['Race Winning driverId'].astype('Int64')
    race_analytics_cols_to_keep['Race Round'] = race_analytics_cols_to_keep['Race Round'].astype('Int64')

    # year has to be an integer, not a float, so that we do not have json files as such: stats_2000.0.json, stats_2001.0.json
    race_analytics_cols_to_keep['year'] = race_analytics_cols_to_keep['year'].astype('Int64')
    data_grouped_by_year = race_analytics_cols_to_keep.groupby('year')
    return data_grouped_by_year


def export_as_json_per_year(data_grouped_by_year, output_path):
    for year, data in data_grouped_by_year:
        data = data.drop(columns=['year'])
        json_output = data.to_dict(orient='records')
        filename = f'{output_path}/stats_{year}.json'

        with open(filename, 'w') as fd:
            json.dump(json_output, fd, indent=2)


def main():
    joined_data = get_data(races_path=RACES_PATH, results_path=RESULTS_PATH)
    data_grouped_by_year = prepare_output(joined_data)
    export_as_json_per_year(data_grouped_by_year, output_path=RESULTS_OUTPUT_PATH)


if __name__ == "__main__":
    main()