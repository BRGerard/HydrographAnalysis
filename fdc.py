"""
Modified from "http://earthpy.org/flow.html"
Date: 2017-03-22
"""
import pandas as pd
import scipy.stats as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rankdata

def fdc(df, clmn, nme, units):
    '''
    Summary: Generate flow duration curve for hydrologic time series data
    Variables:
        * df = Pandas dataframe containing data
        * clmn = Column of flow data.
        * nme = Site and plot file name.
        * units = Flow units (cms or cfs).
    Returns: A flow duraction curve .png file.
    Example:
        > fdc(pd.read_hdf("east_bear_2010-2016.hdf"), "65462_00060", "Test", "cms")
    '''
        
    data = pd.to_numeric(df[clmn], errors = 'coerce')
    data = data[~np.isnan(data)]
    data = np.sort(data)
    ranks = len(data) - rankdata(data, method = "average")
    prob = [100*(ranks[i]/(len(data)+1)) for i in range(len(data))]
    plt.plot(prob, data, linewidth = 4)
    plt.yscale('log')
    plt.grid(which = 'both')
    plt.xlabel('Exceedance Probability (%)', fontsize = 20)
    plt.ylabel('Discharge ({})'.format(units), fontsize = 20)
    plt.title('Flow Duration Curve for {}'.format(nme), fontsize = 25)
    plt.savefig(nme.lower().replace(" ", "_"))
