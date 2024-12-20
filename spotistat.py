#!/usr/bin/python3

import pandas as pd
import numpy as np
import json
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import seaborn
from pandas.api.types import CategoricalDtype
import os
import re

plt.close("all")
seaborn.set()


#plt.ion()

def plot_df(df, x, y, title=None, y_label=None):
    fig, ax = plt.subplots(1, 1)
    ax.bar(x, y, data=df)

    if title is not None:
        ax.set_title(title)
    if y_label is not None:
        ax.set_ylabel(y_label)

    # Major ticks every 6 months.
    fmt_month = mdates.MonthLocator(interval=1)
    ax.xaxis.set_major_locator(fmt_month)

    # Minor ticks every month.
    fmt_day = mdates.DayLocator()
    ax.xaxis.set_minor_locator(fmt_day)

    ax.grid(True)

    # Rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them.
    fig.autofmt_xdate()


def ms2hr(ms_val):
    return ms_val / (1000 * 60 * 60)


def file2data_frame(stream_file_list):
    dfs = []  # list to store DataFrames
    for f_name in stream_file_list:
        with open(f_name, encoding="utf-8") as f:  # Set encoding to read the json file(s)
            json_data = pd.json_normalize(json.loads(f.read()))
            # print(json_data)
            dfs.append(json_data)
    df = pd.concat(dfs, sort=False)  # or sort=True depending on your needs
    return df


def load_over_time(df):
    # convert string datetime to datetime format
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date
    df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))

    # get only date and duration of stream
    df_time = df[['endTime', 'msPlayed']]

    # sum daily hours of spotify 
    df_time_sum = df_time.groupby(['endTime'], as_index=False).agg({'msPlayed': 'sum'})
    df_time_sum['hrPlayed'] = df_time_sum['msPlayed'] / (1000 * 60 * 60)

    #df_time_sum.info()
    return df_time_sum


def avg_day_load(df):
    # convert string datetime to datetime format
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date
    df['date'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))

    # group by date
    df = df.groupby('date', as_index=True).agg({'endTime': 'count', 'msPlayed': 'sum'})
    df = df.asfreq('D', fill_value=0)
    df.reset_index(level=0, inplace=True)

    # add day name column 
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday']
    day_types = CategoricalDtype(categories=days, ordered=True)
    df['weekday'] = df['date'].dt.day_name()
    df['weekday2'] = df['weekday'].astype(day_types)
    df['weekday'] = df['weekday'].astype(day_types)

    # group by day names
    df_week_sum = df.groupby('weekday', as_index=True) \
        .agg({'weekday2': 'count', 'endTime': 'sum', 'msPlayed': 'sum'}) \
        .rename(columns={'endTime': 'noStreams', 'weekday2': 'dayCount'})

    df_week_sum['hrPlayed'] = df_week_sum['msPlayed'] / (1000 * 60 * 60)
    df_week_sum['hrPlayedAvg'] = df_week_sum['hrPlayed'] / df_week_sum['dayCount']
    df_week_sum['noStreamsAvg'] = df_week_sum['noStreams'] / df_week_sum['dayCount']
    df_week_sum['lenStreamsAvgMin'] = df_week_sum['msPlayed'] / df_week_sum['noStreams'] / (1000 * 60)

    print(df_week_sum)

    df_week_sum = df_week_sum.drop(columns=['msPlayed', 'hrPlayed', 'dayCount', 'noStreams'])

    fig = plt.figure()
    ax = fig.add_subplot(231)
    ax2 = fig.add_subplot(232)
    ax3 = fig.add_subplot(233)
    ax.axis('equal')
    ax.pie(df_week_sum['hrPlayedAvg'], labels=days, autopct='%1.2f%%')
    ax.set_title('Average Stream Time per Day')

    ax2.axis('equal')
    ax2.pie(df_week_sum['noStreamsAvg'], labels=days, autopct='%1.2f%%')
    ax2.set_title('Average Nubmer of Streams per Day')

    ax3.axis('equal')
    ax3.pie(df_week_sum['lenStreamsAvgMin'], labels=days, autopct='%1.2f%%')
    ax3.set_title('Average Stream Length per Day')

    axb = fig.add_subplot(234)
    axb2 = fig.add_subplot(235)
    axb3 = fig.add_subplot(236)

    axb.bar(days, df_week_sum['hrPlayedAvg'])  #labels = days,autopct='%1.2f%%')
    axb.set_ylabel('Hours [h]')
    axb2.bar(days, df_week_sum['noStreamsAvg'])  # labels = days,autopct='%1.2f%%')
    axb2.set_ylabel('Number of streams')
    axb3.bar(days, df_week_sum['lenStreamsAvgMin'])  # labels = days,autopct='%1.2f%%')
    axb3.set_ylabel('Length in minutes [min]')
    fig.autofmt_xdate()

    print(df_week_sum)


def top10artists(df, top=10, plot=True):
    print('Top Artists')
    df_top10 = df.groupby('artistName', as_index=False) \
        .agg({'endTime': 'count', 'msPlayed': 'sum'}) \
        .rename(columns={'endTime': 'noStreams', 'msPlayed': 'streamTimeMs'})
    df_top10['streamTimeHr'] = df_top10['streamTimeMs'] / (1000 * 60 * 60)
    df_top10 = df_top10.sort_values(by=['noStreams'], ascending=False)
    df_top10 = df_top10.head(top)

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax2 = ax.twinx()
        ax2.grid(False)

        width = 0.27
        ind = np.arange(len(df_top10))

        bar1 = ax.bar(ind, df_top10['noStreams'], width, color='r',
                      label='Number of Streams')
        bar2 = ax2.bar(ind + width, df_top10['streamTimeHr'], width, color='b',
                       label='Stream Time [hours]')
        fig.legend(loc="upper right")

        ax.set_xticks(ind + width)

        ax.set_xticklabels(df_top10['artistName'])
        ax.set_title(f'Top {top} artists sorted by numer of streams')
        ax.set_ylabel('Number of streams')

        ax2.set_ylabel('Stream time [h]')
        fig.autofmt_xdate()

    print(df_top10)
    return df_top10


def top10tracks(df, top=10, plot=True):
    print('Top Tracks')
    df_top10 = df.groupby(['trackName', 'artistName'], as_index=False) \
        .agg({'endTime': 'count', 'msPlayed': 'sum'}) \
        .rename(columns={'endTime': 'noStreams', 'msPlayed': 'streamTimeMs'})
    df_top10['streamTimeHr'] = df_top10['streamTimeMs'] / (1000 * 60 * 60)
    df_top10 = df_top10.sort_values(by=['noStreams'], ascending=False)
    df_top10 = df_top10.head(top)
    df_top10['fullName'] = df_top10['artistName'] + ' - ' + df_top10['trackName']

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax2 = ax.twinx()
        ax2.grid(False)

        width = 0.27
        ind = np.arange(len(df_top10))

        bar1 = ax.bar(ind, df_top10['noStreams'], width, color='r',
                      label='Number of streams')
        bar2 = ax2.bar(ind + width, df_top10['streamTimeHr'], width, color='b',
                       label='Stream Time [hours]')
        fig.legend(loc="upper right")

        ax.set_xticks(ind + width)
        ax.set_xticklabels(df_top10['fullName'])
        ax.set_title(f'Top {top} songs sorted by numer of streams')
        ax.set_ylabel('Number of streams')

        ax2.set_ylabel('Stream time [h]')
        fig.autofmt_xdate()

    print(df_top10)
    return df_top10


def top10artists_history(df, df_top10, plot=True):
    df_top = df[df['artistName'].isin(df_top10['artistName'])]
    df_top['endTime'] = pd.to_datetime(df_top['endTime'])

    # change datetime format to only date
    df_top['date'] = pd.to_datetime(df_top['endTime'].dt.strftime("%Y-%m-%d"))
    df_top = df_top.groupby(['artistName', 'date'], as_index=False) \
        .agg({'endTime': 'count'}) \
        .rename(columns={'endTime': 'noStreams'})

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for artist in df_top10['artistName']:
            df_tmp = df_top[df_top['artistName'] == artist]
            ax.plot(df_tmp['date'], df_tmp['noStreams'], '-o', label=artist, )
        ax.legend()
        ax.set_title(f'Top {len(df_top10)} artists streaming history')
        ax.set_ylabel('Number of streams')


def top10artists_most_days(df, top=20, plot=True):
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date
    df['date'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))
    df.drop(columns=['msPlayed', 'endTime', 'trackName'], inplace=True)
    df.drop_duplicates(inplace=True)

    df = df.groupby(['artistName'], as_index=False) \
        .agg({'date': 'count'}) \
        .rename(columns={'date': 'days'})
    df.sort_values(by=['days'], ascending=False, inplace=True)

    df = df.head(top)

    if plot:
        width = 0.7
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(f'Top {len(df)} artists streaming history by reoccurring days')
        ax.set_ylabel('Number days')
        bar1 = ax.bar(df['artistName'], df['days'], width, color='r')
        fig.autofmt_xdate()


def main(stream_file_list):
    df = file2data_frame(stream_file_list)

    # Variable name changed since this code was last updated. Renaming columns to reduce renaming multiple var's in
    # the code
    df.rename(columns={'ts': 'endTime', 'master_metadata_album_artist_name': 'artistName',
                       'master_metadata_track_name': 'trackName', 'ms_played': 'msPlayed'}, inplace=True)

    df_time_sum = load_over_time(df)
    plot_df(df_time_sum, 'endTime', 'hrPlayed',
            title=f'Listening time to Spotify streams per day: {df['endTime'].dt.strftime("%Y").iloc[1]} onwards',
            y_label='Hours [h]')  # Needs checking as the year output may be wrong with multiple json inputs

    avg_day_load(df)
    df_top10 = top10artists(df, 30)
    top10tracks(df, 30)
    top10artists_history(df, df_top10.head(5))
    top10artists_most_days(df, 30)
    plt.show()


if __name__ == "__main__":
    all_files = [pos_json for pos_json in os.listdir(os.getcwd())
                 if re.match(r"StreamingHistory\d*\.json$", pos_json)]
    # print(f"All files found: {all_files}")
    if all_files:
        main(all_files)
    else:
        print(f"No JSON file found or no file with the naming conversion StreamingHistory_.json found")
