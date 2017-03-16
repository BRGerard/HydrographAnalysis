# -*- coding: utf-8 -*-
"""
Created: 20160502
Last Modified: 20170123
Creator: B.Gerard
Comments: A script to download archived flow data from the USGS.
"""
from urllib.request import urlopen
import urllib
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
#===================================================================================================
# Go to URL, download the data, write the data to file.
#===================================================================================================
dict = {
    'east_bear':'01022294',
    'otter':'01022840',
    'ducktrap':'01037380',
    'libby':'01021470',
    'branch':'01069700',
    'stoney':'01063310', 
    'old_str':'01021480',
    'kennebunk':'01067950',
    'east_wess':'01048220',
    'black_str':'01031510',
    'pearce':'01018009',
    'williams':'01017550',
    'hardwood':'01017060',
    'sandy':'01047200'
}
def Scrapper(strdate,enddate,year):
    for key in dict.keys():
        print("{}: {}". format(year, key))
        if "{}_{}.txt".format(key, year) in os.listdir():
            pass
        else:
            file = urlopen("http://nwis.waterdata.usgs.gov/me/nwis/uv?cb_00065=on&cb_00060=on&format=rdb&site_no={}&period=&begin_date={}&end_date={}".format(dict[key],strdate,enddate))
            with open("{}_{}.txt".format(key, year), "wb") as code:
                        code.write(file.read())
                        file.close()

for i in range(2010, 2017):
    Scrapper('{}-01-01'.format(i),'{}-12-31'.format(i),i)

#===================================================================================================
# Compile and concatenate datafiles.
#===================================================================================================

# CREATE ALL DATAFRAMES #
dfs = {}
for key in dict.keys():
    dfs[key] = pd.DataFrame()

def usgs_parse(nfle):
    data_fle = open(nfle)
    count = 0
    for line in data_fle:
        if line[:9] == "agency_cd":
            skp = count
            break
        count += 1
        
    data_df = pd.read_csv(nfle, sep = '\t', skiprows = skp, index_col = [2])
    data_df = data_df.drop(data_df.index[0])
    data_df.index = data_df.index.to_datetime()
    return data_df

# LOOP THROUGH FLES AND GROUP SITES #
for fle in sorted(os.listdir()):
    if '.txt' in fle and "README.txt" != fle:
        data = usgs_parse(fle)
        dfs[fle[:-9]] = dfs[fle[:-9]].append(data)
        dfs[fle[:-9]] = dfs[fle[:-9]].groupby(dfs[fle[:-9]].index).first()
        print(fle)
        print(data.head())

#===================================================================================================
# Write out datafles.
#===================================================================================================
for key in dfs.keys():
    dfs[key].to_hdf("{}_2010-2016.hdf".format(key), "df")
