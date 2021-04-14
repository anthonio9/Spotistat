# Spotistat

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


### Install required packages (pandas, numpy, seabord, matplotlib)

```sh
pip install -r required.txt
```

## Run

Spotify lets you download zip with your data, there is `one` or more files containing you **streaming history**, these are called `StreamingHistoryX`, where `X` is a number. 
Run the `spotistat.py` script followed by path to all of you `StreamingHistoryX` files.

Example:

```sh
python3 spotistat.py '../MyData/StreamingHistory0.json' '../MyData/StreamingHistory1.json'
```
