 seabord# Spotistat

This is a simple python script printing pretty plots and charts based on **Spotify streaming history** data. Now you too can check the number of times you listened to your favourite song, before Spotify End's Year Summary!
Isn't this awesome?

By the way, watch this [video](https://youtu.be/HYEe1j3CCA8) if you're interested in how this repo came to be.

## Prepare an environment

### Linux

1. Download Python3 and install pip

* Ubuntu:

```sh
sudo apt-get install python3
sudo apt install python3-pip
```

* Centos:

```sh
sudo yum install python3
```

* Manjaro:

```sh
sudo pacman -S python3
sudo pacman -S python-pip
```


### Windows

1. Download Python3

	Look [here](https://www.python.org/downloads/windows/). 

2. Install pip

	Look [here](https://www.liquidweb.com/kb/install-pip-windows/)


### Install required packages (pandas, numpy, seaborn, matplotlib)

```sh
pip install -r required.txt
```

or

```sh
pip install pandas numpy seaborn matplotlib
```

## Run

Spotify lets you download your data - [Link to request Data from Spotify](https://www.spotify.com/in-en/account/privacy/).
You should receive `one` or more files containing your **streaming history** (files will be in json), and will be in a format `StreamingHistoryX`, where `X` is a number. 
Run the `spotistat.py` from the same directory where `StreamingHistoryX` json files are stored.

Note that you may have to rename the Streaming History files to the required format, which is "StreamingHistoryX.json" where X should be a unique digit

Example:

```sh
python3 spotistat.py
```
