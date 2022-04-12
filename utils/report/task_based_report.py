#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 10:36:43 2021

@author: c00424072
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

schedulers = ['MM','EE','FairEE']
n = len(schedulers)
capacity = 35.0
workload = '6-2'

task_types = ['TT1', 'TT2']
machine_types = ['cpu', 'gpu']

i = 0
#fig, ax = plt.figure()
fig, ax = plt.subplots()
#ax = fig.add_axes([0,0,1,1])
width = 0.15
d = 1*width
r0= 0
r = []
hatch = [['xx','xx'] ,[ 'oo', 'oo'],['\\\\','\\\\']]
colors = [['darkred', 'navy'], ['orange', 'darkgreen'],['indigo', 'lightseagreen']]

for scheduler in schedulers:
    path = f'./results/data/workload-{workload}/{scheduler}/task_based_report.csv'
    
    df = pd.read_csv(path)
    df['TT1_cpu-1_total_completed'] = df['TT1_completed_cpu-1'] + df['TT1_xcompleted_cpu-1']
    df['TT2_cpu-1_total_completed'] = df['TT2_completed_cpu-1'] + df['TT2_xcompleted_cpu-1']
    
    df['TT1_cpu-2_total_completed'] = df['TT1_completed_cpu-2'] + df['TT1_xcompleted_cpu-2']
    df['TT2_cpu-2_total_completed'] = df['TT2_completed_cpu-2'] + df['TT2_xcompleted_cpu-2']
    
    df['TT1_cpu-3_total_completed'] = df['TT1_completed_cpu-3'] + df['TT1_xcompleted_cpu-3']
    df['TT2_cpu-3_total_completed'] = df['TT2_completed_cpu-3'] + df['TT2_xcompleted_cpu-3']
    
    df['TT1_cpu-4_total_completed'] = df['TT1_completed_cpu-4'] + df['TT1_xcompleted_cpu-4']
    df['TT2_cpu-4_total_completed'] = df['TT2_completed_cpu-4'] + df['TT2_xcompleted_cpu-4']
    
    df['TT1_gpu_total_completed'] = df['TT1_completed_gpu'] + df['TT1_xcompleted_gpu']
    df['TT2_gpu_total_completed'] = df['TT2_completed_gpu'] + df['TT2_xcompleted_gpu']
    
    df['TT1_cpu_total_completed'] = 0
    df['TT2_cpu_total_completed'] = 0
    
    for k in range(1,5):
        df['TT1_cpu_total_completed'] += df[f'TT1_cpu-{k}_total_completed'] 
        df['TT2_cpu_total_completed'] += df[f'TT2_cpu-{k}_total_completed'] 
        
    mean_values = df.mean(axis=0)    
    
    
    # cpu = df.loc[:,['TT1_assigned_to_cpu', 'TT2_assigned_to_cpu']]
    # gpu = df.loc[:,['TT1_assigned_to_gpu', 'TT2_assigned_to_gpu']]
    
    cpu = df.loc[:,['TT1_cpu_total_completed', 'TT2_cpu_total_completed']]
    gpu = df.loc[:,['TT1_gpu_total_completed', 'TT2_gpu_total_completed']]
    
    # cpu1 = cpu1.mean(axis=0).values
    # cpu2 = cpu2.mean(axis=0).values
    # cpu3 = cpu3.mean(axis=0).values
    # cpu4 = cpu4.mean(axis=0).values
    
    cpu = cpu.mean(axis=0).values    
    gpu = gpu.mean(axis=0).values
    #not_assigned = [(1 - gpu[0] - cpu[0]), (1 - gpu[1] - cpu[1])]
     
        

   
    
    r.append([ r0+i*width,r0+ (n+i)*width + d]) # the x locations for the groups
    
    plt.bar(r[i], cpu, width,label=f'CPU-{scheduler}',
           edgecolor=colors[i][0], fill = False, hatch=hatch[i][0]
           )
    
    # plt.bar(r[i], cpu2, width,bottom=cpu1,label=f'CPU-2-{scheduler}',
    #        edgecolor=colors[i][0], fill = False, hatch=hatch[i][0])
    
    # plt.bar(r[i], cpu3, width,bottom=cpu1+cpu2,label=f'CPU-3-{scheduler}',
    #        edgecolor=colors[i][0], fill = False, hatch=hatch[i][0])
    
    # plt.bar(r[i], cpu4, width,bottom=cpu1+cpu2+cpu3,label=f'CPU-4-{scheduler}',
    #        edgecolor=colors[i][0], fill = False, hatch=hatch[i][0])
    
    
    plt.bar(r[i], gpu, width,bottom=cpu,label = f'GPU-{scheduler}',
           edgecolor=colors[i][1], fill = False, hatch =hatch[i][1]
           )
    
    #ax.set_xticklabels(task_types)
    #ax.set_yticks(np.arange(0, 81, 10))
    
    i+=1
#ax.set_ylim(0,100)
plt.ylabel('Assignment%')
plt.title('Task Types')
plt.xticks([r0+(n-1)*0.5*width, r0+(n-1)*0.5*width + n*width+d ])
ax.set_xticklabels(task_types)
#plt.legend()
l5 = plt.legend(bbox_to_anchor=(1.0,1), loc="upper left", 
                 ncol=1)
plt.savefig('./results/figures/task_based_assignment_6-2_just_for_TT1.pdf', 
            bbox_inches='tight',dpi=300)
plt.show()