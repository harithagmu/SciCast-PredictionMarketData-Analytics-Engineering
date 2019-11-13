import pandas as pd
import os

os.chdir("D:\\Fall 2019\\CAP\\weighted avg")
data = pd.read_csv("usersBigdata.csv")
data.groupby('category1', as_index=False)['error'].mean()
