#!etc/bin/bash

wget http://github.com/bbuchfink/diamond/releases/download/v2.0.13/diamond-linux64.tar.gz
tar xzf diamond-linux64.tar.gz
rm diamond-linux64.tar.gz

# Download the database
# Store preindexed diamond db in google drive and prep a download link
wget "https://drive.google.com/uc?export=download&id=1uhu7Il-thPwUn4Vw2mAvttupc9wyQJw6&confirm=t" -O plants_all.dmnd
