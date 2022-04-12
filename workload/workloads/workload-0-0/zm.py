import pandas as pd

df = pd.read_csv('workload-0.csv')
task_type_id = df.loc[1,'task_type_id']

print(task_type_id)