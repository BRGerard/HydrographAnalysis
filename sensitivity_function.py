# -*- coding: utf-8 -*-
"""
Created: 20151203
Modified: 20170125
Creator: Brett Gerard
Comments: This script analyzes baseflow recession limbs to evaluate linear 
reservoir time constants and storage depths.
"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from scipy import stats
import pandas as pd
import os
#===================================================================================================
# Define the flow index and set the variables.
#===================================================================================================
dict = {
    'east_bear':['65462_00060', 'East Bear Brook: USGS 01022294', '570794.3', '4967687.9', '0.11'],
    'otter':['65475_00060', 'Otter Creek: USGS 01022840', '563248.3', '4909140.8', '3.50'],
    'ducktrap':['65572_00060', 'Ducktrap River: USGS 01037380', '495149.8', '4908435.5', '37.40'],
    'libby':['65452_00060', 'Libby Brook: USGS 01021470', '600837.1', '4961616.5', '20.18'],
    'branch':['65774_00060', 'Branch Brook: USGS 01069700', '371740.5', '4804139.3', '27.71'],
    'stoney':['65728_00060', 'Stoney Brook: USGS 01063310', '368217.5', '4857136.5', '2.10'],
    'old_str':['65456_00060', 'Old Stream: USGS 01021480', '599723.0', '4976722.7', '75.37'],
    'kennebunk':['65763_00060', 'Kennebunk River: USGS 01067950', '374280.6', '4809985.9', '69.15'],
    'east_wess':['65632_00060', 'East Branch Wesserunsett: USGS 01048220', '448175.5', '4977328.2', '50.50'],
    'black_str':['65540_00060', 'Black Stream: USGS 01031510', '481417.7', '4999671.8', '67.34'],
    'pearce':['65395_00060', 'Pearce Brook: USGS 01018009', '589613.1', '5107509.5', '20.69'],
    'williams':['65383_00060', 'Williams Brook: USGS 01017550', '580145.0', '5164364.9', '9.89'],
    'hardwood':['65375_00060', 'Hardwood Brook: USGS 01017060', '577158.7', '5184614.1', '14.76'],
    'sandy':['65622_00060', 'Sandy River: USGS 01047200', '382648.1', '4968224.5', '65.53'] 
}

#VARIABLES
timestep = "1H"


#===================================================================================================
# Bring in data from various sources.
#===================================================================================================
site={}
for file in sorted(os.listdir()):
    if 'hdf' in file:
        name = file.replace('_2010-2016.hdf','')
        site[name] = (pd.read_hdf(file))
        site[name] = site[name][[dict[name][0]]]
        site[name][dict[name][0]] = pd.to_numeric(site[name][dict[name][0]], errors = 'coerce')
        site[name] = site[name].resample(timestep).mean()
        site[name].insert(len(site[name].columns),'discharge_cms',(site[name][dict[name][0]]*0.028)/(float(dict[name][4])*1000000))
        
#===================================================================================================
# Select time periods not in winter and during the night.
#===================================================================================================
for key in site:
    for yr in range(2010, 2017):
        site[key] = (site[key].drop(site[key].ix['{}-11-01'.format(yr):'{}-03-01'.format(yr)].index)).between_time('07:00','19:00')
        
#===================================================================================================
# Analyze the recession limb.
#===================================================================================================
results = {}
for key in site:
    nmbr = len(site[key])
    results['{}_Q'.format(key)] = []
    results['{}_dQdt'.format(key)] = []
    a = -1
    c = 1
    for b in range(nmbr):
        if c == -1:
            pass
        if c == nmbr:
            break
        results['{}_Q'.format(key)].append(site[key].discharge_cms[b])
        results['{}_dQdt'.format(key)].append(-(site[key].discharge_cms[b]-site[key].discharge_cms[a])/(timedelta.total_seconds(site[key].index[b]-site[key].index[a])))
        a+=1
        c+=1
        print('{}: {}'.format(key,site[key].index[a]))

        
#===================================================================================================
# Run Statistics and Plot Data.
#===================================================================================================
def RecStatistics(location, title, fig_ttle):
    df = pd.DataFrame({'{}_Q'.format(location):results['{}_Q'.format(location)], '{}_dQdt'.format(location):results['{}_dQdt'.format(location)]})
    df = df[(df['{}_Q'.format(location)] > 0) & (df['{}_dQdt'.format(location)] > 0)]
    slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(df['{}_Q'.format(location)]),np.log(df['{}_dQdt'.format(location)]))

    x=[]
    y=[]
    xmin = np.min(df['{}_Q'.format(location)])
    xmax = np.max(df['{}_Q'.format(location)])
    ymin = np.min(df['{}_dQdt'.format(location)])
    ymax = np.max(df['{}_dQdt'.format(location)])
    for i in np.arange(xmin, xmax, xmin):
            y.append(np.e**(intercept+slope*np.log(i)))
            x.append(i)
    
    fig = plt.figure(figsize = (25,15))
    plt.plot(x,y,color='black',linewidth = 4)
    plt.scatter(df['{}_Q'.format(location)], df['{}_dQdt'.format(location)])
    plt.xlabel('DA Normalized Discharge ($m/s$)',fontsize = 40)
    plt.ylabel('-dQ/dt ($m/s^2$)',fontsize = 40)
    plt.title("{}".format(title),fontsize = 40)
    plt.xscale('log')
    plt.yscale('log')
    plt.yticks(fontsize = 35)
    plt.xticks(fontsize = 35)
    plt.annotate('y = %s $x^{%.2f}$ \n$R^2$ = %s' % ("{:.2e}".format(np.e**intercept), round(slope,2), round(r_value,2)), xy = (0.05, 0.85), xycoords = 'axes fraction', fontsize = 50)
    plt.subplots_adjust(left = 0.25, right = 0.75, top = 0.9, bottom = 0.1)
    fig.savefig(fig_ttle)
    return slope

newfile = open("results.csv", "w")
newfile.write("Site, Easting, Northing, Slope\n")
for key in sorted(site.keys()):
    slope = RecStatistics(key, dict[key][1], '{}_func.png'.format(key))
    newfile.write("{}, {}, {}, {}\n".format(key, dict[key][2], dict[key][3], slope))
newfile.close()
