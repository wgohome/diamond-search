#!etc/bin/bash

wget http://github.com/bbuchfink/diamond/releases/download/v2.0.13/diamond-linux64.tar.gz
tar xzf diamond-linux64.tar.gz
rm diamond-linux64.tar.gz

# Download the database
# Store preindexed diamond db in google drive and prep a download link
wget "https://drive.google.com/uc?export=download&id=1OL3TqKRHEwmklJFziBkd9BWeHZYZvw4y&confirm=t" -O plants_all.dmnd
