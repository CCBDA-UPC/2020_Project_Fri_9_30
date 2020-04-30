# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


def change_path():
    path = 'C:\\Users\\Ariston\\Desktop\\jupytercsv'
    os.chdir(path)
    
def animate(i):
    f = pd.read_csv('covid_summary_sample.csv')
    
    ax1.clear()
    ax1.plot(f['day'], f['cases'])

    plt.xlabel('Day')
    plt.ylabel('Cases')
    plt.title('Live graph with matplotlib')
    

change_path()
style.use('fivethirtyeight')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ani = animation.FuncAnimation(fig, animate, interval=1000) 
plt.show()
    