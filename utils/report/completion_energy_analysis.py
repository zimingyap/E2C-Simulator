#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 09:48:42 2021

@author: c00424072
"""

import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats
import numpy as np



def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return h
    


schedulers = ['EE','MM']

task_hete = 4

df_summary = pd.DataFrame(data=None, columns = ['rate-id','scheduler' ,'totalCompletion%',
                                                'consumed_energy%','energy_per_completion'])

hatch = ['xxx','\\\\\\\\']
colors = ['navy','darkred']


for scheduler in schedulers:
        
    for rate in range(2,8):
    
        workload = f'workload-{rate}-{task_hete}'
        path = f'./results/data/{workload}/{scheduler}/results-summary.csv'
        df = pd.read_csv(path)
        d = df.mean().loc[['totalCompletion%','consumed_energy%','energy_per_completion']]
        d['rate-id'] = int(rate)        
        d['scheduler'] = scheduler
        d['CI'] = mean_confidence_interval(df['energy_per_completion'])
        df_summary = df_summary.append(d, ignore_index=True)
        df_summary['rate-id'] = df_summary['rate-id'].astype('int')
    
x = df_summary[df_summary['scheduler']==scheduler]['rate-id'].values

width = 0.5
dist = 1.0

rate_label = ['{0:1.1f}'.format(1000/(1000-i*100)) for i in range(2,8)]
#r = x - 0.5 * width
r0 = 0
r = [(r0-0.5*width+i*(2*width+dist)) for i in range(2,8)]
i = 0
plt.figure()
for scheduler in schedulers:
    #x = r + i*width
    r = [r[k] + i*width for k in range(len(r))]
    print(r)
    y = df_summary[df_summary['scheduler']==scheduler]['energy_per_completion'].values
    yerr = df_summary[df_summary['scheduler']==scheduler]['CI'].values
    
    plt.bar(r,y,yerr=yerr, width= width, capsize=2,fill=True,color='white',zorder=10,
            hatch = hatch[i],edgecolor=colors[i],label=scheduler)
    i+=1
r = [r[k] - (i-1)*width+0.5*width for k in range(len(r))]
plt.xticks(r,rate_label )
plt.xlabel('Arrival Rate [#tasks/second]')
plt.ylabel('Energy Usage per Task Completion')
plt.legend()
plt.grid(axis='y')
#plt.savefig(f'./results/figures/energy_per_completion_task_hete-{task_hete}.pdf',dpi=300)
    

####################################################################
# =============================================================================
# fig = plt.figure()
# ax1 = fig.add_subplot(111)
# 
# markers = ['o', 'x', '<', 's']
# 
# 
# df = pd.read_csv('./workload-8-3-completion-vs-energy.csv')
# 
# 
# i=0
# for scheduler in schedulers:
#     
#     y = df[scheduler+'-completion'].astype(float)    
#     x = 3.6*(df[scheduler+'-energy_consumption'].astype(float))
#     
#     ax1.plot(x.values, y.values, marker = markers[i],
#              color = colors[i],
#              linestyle ='--',
#              label = scheduler)
#     i += 1
#     
#     
# 
# 
# 
# plt.legend()
# plt.xlabel('Available Energy (KJ)')
# plt.ylabel('%Completion')
# plt.grid()
# 
# plt.savefig('./results/figures/completion_vs_energy_8-3.pdf',dpi=300)
# plt.show()
# =============================================================================




