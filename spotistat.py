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

plt.close("all")

# this package makes things look prettier
seaborn.set()

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
    return ms_val/(1000*60*60)

def file2df(stream_file_list):
    dfs = []

    for f_name in stream_file_list:
        with open(f_name) as f:
            json_data = pd.json_normalize(json.loads(f.read()))
            dfs.append(json_data)
    df = pd.concat(dfs, sort=False) # or sort=True depending on your needs

    return df

def load_over_all_time(df):
    # convert string datetime to datetime format
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date, remember to keep the datatime format
    df['endTime'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))

    # get only date and duration of stream
    df_time = df[['endTime', 'msPlayed']]

    # sum daily played time of spotify, group by endTime, then sum all the records
    df_time_sum = df_time.groupby(['endTime'], as_index=False).agg({'msPlayed': 'sum'})

    # count number of hours played every day
    df_time_sum['hrPlayed'] = ms2hr(df_time_sum['msPlayed'])

    return df_time_sum

def avg_weekday_load(df):
    # convert string datetime to datetime format
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date, keep the dataframe format
    df['date'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))

    # group by date
    df = df.groupby('date', as_index=True).agg({'endTime':'count', 'msPlayed':'sum'})

    # fill-in missing days, fill them with 0 msPlayed
    df = df.asfreq('D', fill_value=0)
    df.reset_index(level=0, inplace=True)

    # add day name column 
    days = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday', 'Sunday']
    day_types = CategoricalDtype(categories=days, ordered=True)
    df['weekday'] = df['date'].dt.day_name()
    df['weekday2'] = df['weekday'].astype(day_types)
    df['weekday'] = df['weekday'].astype(day_types)

    # group by day names
    df_week_sum = df.groupby('weekday', as_index=True) \
            .agg({'weekday2':'count', 'endTime':'sum', 'msPlayed':'sum'}) \
            .rename(columns={'endTime':'noStreams', 'weekday2':'dayCount'})

    df_week_sum['hrPlayed'] = ms2hr(df_week_sum['msPlayed'])
    df_week_sum['hrPlayedAvg'] = df_week_sum['hrPlayed']/df_week_sum['dayCount']
    df_week_sum['noStreamsAvg'] = df_week_sum['noStreams']/df_week_sum['dayCount']
    df_week_sum['lenStreamsAvgMin'] = df_week_sum['msPlayed']/ms2hr(df_week_sum['noStreams'])

    print(df_week_sum)

    # this isn't necessary
    df_week_sum = df_week_sum.drop(columns=['msPlayed', 'hrPlayed', 'dayCount', 'noStreams'])

    fig = plt.figure()
    ax = fig.add_subplot(231)
    ax2 = fig.add_subplot(232)
    ax3 = fig.add_subplot(233)
    ax.axis('equal')
    ax.pie(df_week_sum['hrPlayedAvg'], labels = days,autopct='%1.2f%%')
    ax.set_title('Average Stream Time per Day')

    ax2.axis('equal')
    ax2.pie(df_week_sum['noStreamsAvg'], labels = days,autopct='%1.2f%%')
    ax2.set_title('Average Nubmer of Streams per Day')

    ax3.axis('equal')
    ax3.pie(df_week_sum['lenStreamsAvgMin'], labels = days,autopct='%1.2f%%')
    ax3.set_title('Average Stream Length per Day')

    axb = fig.add_subplot(234)
    axb2 = fig.add_subplot(235)
    axb3 = fig.add_subplot(236)

    axb.bar(days, df_week_sum['hrPlayedAvg']) #labels = days,autopct='%1.2f%%')
    axb.set_ylabel('Hours [h]')
    axb2.bar(days, df_week_sum['noStreamsAvg'])# labels = days,autopct='%1.2f%%')
    axb2.set_ylabel('Number of streams')
    axb3.bar(days, df_week_sum['lenStreamsAvgMin'])# labels = days,autopct='%1.2f%%')
    axb3.set_ylabel('Length in minutes [min]')
    fig.autofmt_xdate()

    print(df_week_sum)

def top_artists(df, top=10, plot=True):
    print('Top Artists')
    df_top = df.groupby('artistName', as_index=False) \
        .agg({'endTime':'count', 'msPlayed':'sum'}) \
        .rename(columns={'endTime':'noStreams', 'msPlayed':'streamTimeMs'})
    df_top['streamTimeHr'] = ms2hr(df_top['streamTimeMs'])
    df_top = df_top.sort_values(by=['noStreams'], ascending=False)
    df_top = df_top.head(top)

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax2 = ax.twinx()
        ax2.grid(False)
        
        width = 0.27
        ind = np.arange(len(df_top))

        bar1 = ax.bar(ind, df_top['noStreams'], width, color='r',
                      label='Number of Streams')
        bar2 = ax2.bar(ind + width, df_top['streamTimeHr'], width, color='b',
                      label='Stream Time [hours]')
        fig.legend(loc="upper right")

        ax.set_xticks(ind+width)

        ax.set_xticklabels( df_top['artistName'])
        ax.set_title(f'Top {top} artists sorted by numer of streams')
        ax.set_ylabel('Number of streams')

        ax2.set_ylabel('Stream time [h]')
        fig.autofmt_xdate()

    print(df_top)
    return df_top

def top_tracks(df, top=10, plot=True):
    print('Top Tracks')
    df_top10 = df.groupby(['trackName', 'artistName'], as_index=False) \
        .agg({'endTime':'count', 'msPlayed':'sum'}) \
        .rename(columns={'endTime':'noStreams', 'msPlayed':'streamTimeMs'})
    df_top10['streamTimeHr'] = ms2hr(df_top10['streamTimeMs'])
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

        ax.set_xticks(ind+width)
        ax.set_xticklabels( df_top10['fullName'])
        ax.set_title(f'Top {top} songs sorted by numer of streams')
        ax.set_ylabel('Number of streams')

        ax2.set_ylabel('Stream time [h]')
        fig.autofmt_xdate()

    print(df_top10)
    return df_top10

def top_artists_history(df, df_top10, plot=True):
    # get only those artists that are in given df_top10 dataframe
    df_top = df[df['artistName'].isin(df_top10['artistName'])]
    df_top['endTime'] = pd.to_datetime(df_top['endTime'])

    # change datetime format to only date
    df_top['date'] = pd.to_datetime(df_top['endTime'].dt.strftime("%Y-%m-%d"))
    df_top = df_top.groupby(['artistName', 'date'], as_index=False) \
        .agg({'endTime':'count'}) \
        .rename(columns={'endTime':'noStreams'})

    if plot:
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for artist in df_top10['artistName']:
            df_tmp = df_top[df_top['artistName'] == artist]
            ax.plot(df_tmp['date'], df_tmp['noStreams'], '-o', label = artist, )
        ax.legend()
        ax.set_title(f'Top {len(df_top10)} artists streaming history')
        ax.set_ylabel('Number of streams')

def top_artists_most_days(df, top=20, plot=True):
    df['endTime'] = pd.to_datetime(df['endTime'])

    # change datetime format to only date
    df['date'] = pd.to_datetime(df['endTime'].dt.strftime("%Y-%m-%d"))
    df.drop(columns=['msPlayed', 'endTime', 'trackName'], inplace=True)
    df.drop_duplicates(inplace=True)
    
    df = df.groupby(['artistName'], as_index=False) \
            .agg({'date':'count'}) \
            .rename(columns={'date':'days'})
    df.sort_values(by=['days'], ascending=False, inplace=True)

    df = df.head(top)

    if plot:
        width = 0.7
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(f'Top {len(df)} artists streaming history by reccuring days')
        ax.set_ylabel('Number days')
        bar1 = ax.bar(df['artistName'], df['days'], width, color='r')
        fig.autofmt_xdate()

def main(stream_file_list):
    # convert all StreamingHistory files to one data frame
    df = file2df(stream_file_list)

    # get dataframe with spotify listening time per day
    df_time_sum = load_over_all_time(df)
    plot_df(df_time_sum, 'endTime', 'hrPlayed', title='Listening time to Spotify streams per day: 2020/2021', y_label='Hours [h]' )

    df_weekday_sum = avg_weekday_load(df)
    df_top10 = top_artists(df, 30)
    top_tracks(df, 30)
    top_artists_history(df, df_top10.head(5))
    top_artists_most_days(df, 30)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        print(f'sys: {sys.argv[1:]}')
        main(sys.argv[1:])
