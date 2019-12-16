
#Importing required libraries
import psycopg2
import pandas as pd 
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report 
import os
import math

from scipy import interpolate
%matplotlib qt

#Changing the working directory
os.getcwd()
os.chdir("")

#connecting to postgres SQL
conn = psycopg2.connect("")
cursor = conn.cursor()

#Extracting all the binary resolved questions
sql_command = "SELECT * FROM {};".format(str('questions'))
data = pd.read_sql(sql_command, conn)
new_data=data[data.settled_value.isnull() == False]
df=new_data.reset_index(drop=True)
df_binary=df[df.type == 'binary']
df_b=df_binary.reset_index(drop=True)

#Calculating weights for timeline resolution

def find_a_k(d):
    '''
    The function returns constant values of a and k for every unique question 
    using the duration(no. of days) for which the question was open. The function
    assumes equation f(t)=a*(exp(kt)) where f(t)=1 for t=1 and f(t)=100 for t=d(number of days)
    '''
    a=pow(100,(1/(d+1)))
    k=np.log(a)
    return a,k

e=2.718
def exp(t,a,k):
    '''
    The function returns the value of f(t) where f(t)=a*(exp(kt))
    '''
    y=a*(e**(k*t))
    return y

df_time=pd.DataFrame()
df_time['q_id']=df_b['id']    
df_time['creation']=df_b['created_at']
df_time['settled']=df_b['settled_at']
df_time['settled_value']=df_b['settled_value']

#calculating constants a and k for each question
df_time['d']=0
df_time['a']=0.0
df_time['k']=0.0

for i in range(len(df_time)):
    df_time['d'][i]=(df_time['creation'][i]-df_time['settled'][i]).days
    df_time['a'][i],df_time['k'][i]=find_a_k(df_time['d'][i])
    
#Simple Average and Weighted Average for all binary resolved questions


#getting all trades
sql_command = "select h.new_value,h.created_at as h_time,h.question_id,h.user_id,q.created_at as q_time,q.settled_at as q_settledtime,q.settled_value as settled_value from questions q, historical_trades h where q.id=h.question_id and q.settled_value is not null and q.type='binary'and h.user_id!=1 ;"
cat13=pd.read_sql(sql_command, conn)

#Calculating difference between creation time of question and creation time of trade
# As well as difference between creation time of trade and resolution time of question
l=[]
m=[]
l1=[]
for i in range(len(cat13)):
    l.append((cat13['q_time'][i]-cat13['h_time'][i]).days)
    m.append(abs((cat13['q_time'][i]-cat13['h_time'][i]).days))
    l1.append(abs((cat13['h_time'][i]-cat13['q_settledtime'][i]).days))

cat13['t']=l
cat13['t1']=m
cat13['res_time_difference']=l1


#Scaling the resolution value for all questions so that all questions are resolved to a single value
n=[]
for i in range(len(cat13)):
    if cat13['settled_value'][i]==0:
        n.append(1-cat13['new_value'][i])
    else:
        n.append(cat13['new_value'][i])
cat13['new_value_scaled']=n
cat13['Abs Error']=1-cat13['new_value_scaled']

#Timeline weights calulation and scaling the weights
f=[]
for i in range(len(cat13)):
    for j in range(len(df_time)):
        if cat13['question_id'][i]==df_time['q_id'][j]:
            x=exp(cat13['t'][i],df_time['a'][j],df_time['k'][j])
            break
    f.append(x)

cat13['w_unscaled']=f
cat13['w']=cat13['w_unscaled']/100
cat13['w'] 


#plot for checking trend of trades with respect to timeline of question
df_mod=cat13

a=[]
for i in range(len(df_mod)):
    a.append(abs((df_mod['q_settledtime'][i]-df_mod['q_time'][i]).days))
df_mod['length_of_question']=a

df_mod1=df_mod.groupby(['question_id']).mean()
df_mod1=df_mod1.reset_index()
mean_value=math.ceil(df_mod1['length_of_question'].mean())

df_mod['x']=round((df_mod['t1']/df_mod['length_of_question'])*mean_value)
df_mod['x1']=round((df_mod['res_time_difference']/df_mod['length_of_question'])*mean_value)
df_mod['Abs Error']=abs(df_mod['new_value']-df_mod['settled_value'])

df_mod2=df_mod.groupby('x1').mean()
df_mod2=df_mod2.reset_index()
plt.scatter(df_mod2['x1'],df_mod2['Abs Error'])
z = np.polyfit(df_mod2['x1'], df_mod2['Abs Error'], 1)
p = np.poly1d(z)
plt.plot(df_mod2['x1'],p(df_mod2['x1']),"r--")
plt.xlim(max(df_mod['x1']),0)
plt.xlabel("Time until resolution(scaled)")
plt.ylabel("Average Absolute Error")
plt.title("Trend of predictions over time")
plt.grid(True)
plt.show()
#df_mod2.to_csv('df_mod2.csv')

#Calculating weighted Average and simple Average
cat13['prod_time']=cat13['w']*cat13['new_value_scaled']
l=cat13.groupby(['question_id']).mean()
l=l.reset_index()

new_frame_cat13=cat13.groupby(['question_id']).sum()
new_frame_cat13=new_frame_cat13.reset_index()
settled=[]
for i in range(len(new_frame_cat13)):
    if new_frame_cat13['settled_value'][i]==0:
        settled.append(0)
    else:
        settled.append(1)
new_frame_cat13['settled_value']=settled
new_frame_cat13['avg']=l['new_value_scaled']
new_frame_cat13['Weighted_avg_time']=new_frame_cat13['prod_time']/new_frame_cat13['w']
new_frame_cat13['Avg_AE']=1-new_frame_cat13['avg']
new_frame_cat13['WeightedAvg_AE_time']=1-new_frame_cat13['Weighted_avg_time']

#Baseline 1- getting prediction made by the user prior to resolution of question
base=pd.read_csv('basline.csv')
lll=[]
sv=[]
for i in range(len(new_frame_cat13)):
    for j in range(len(base)):
        if base['id'][j]==new_frame_cat13['question_id'][i]:
            lll.append(base['absError'][j])
            sv.append(base['settled_value'][j])
            break
        
new_frame_cat13['baseline_AE']=lll
new_frame_cat13['baseline_settled']=sv
new_frame_cat13['baseline']=abs(new_frame_cat13['baseline_settled']-new_frame_cat13['baseline_AE'])

#Baseline 2- getting last 10 predictions prior to resolution
newavg10 = []
weights=[]
prod=[]
for qid in new_frame_cat13['question_id']:
    records = cat13[cat13.question_id == qid]
    records = records.reset_index()
    #print(records.shape)
    if(len(records)>0):
        if records.shape[0] > 10:
            records = records.sort_values('h_time', ascending= False)
            records = records.reset_index()
            records = records[:10]
            newavg10.append(abs(records['settled_value']-records['new_value']).mean())
            weights.append(sum(records['w']))
            prod.append(sum(records['prod_time']))
        else:
            newavg10.append(abs(records['settled_value']-records['new_value']).mean())
            prod.append(sum(records['prod_time']))
            weights.append(sum(records['w']))
    else:
        newavg10.append(0)
        weights.append(sum(records['w']))
        prod.append(sum(records['prod_time']))
        

wadf=pd.DataFrame()
wadf['prod']=prod
wadf['weights']=weights
wadf['wa']=wadf['prod']/wadf['weights']
new_frame_cat13['baseline_last10'] = newavg10
new_frame_cat13['baseline_last10_wa'] = wadf['wa']
new_frame_cat13['baseline_last10_wa_ae'] = 1-wadf['wa']

#Difference between Simple Average and weighted Average considering both weights as well as only time weights
new_frame_cat13['dff_SA&WA_time_AE']=new_frame_cat13['Avg_AE']-new_frame_cat13['WeightedAvg_AE_time']
plt.plot(new_frame_cat13.index,new_frame_cat13['dff_SA&WA_time_AE'],'o')
plt.axhline(0)

#Mean absolute errors for all the questions
round(new_frame_cat13['Avg_AE'].mean(),2)    #Simple Average 
round(new_frame_cat13['WeightedAvg_AE_time'].mean(),2) #Weighted Average using time weights only
round(new_frame_cat13['baseline_AE'].mean(),2)       #Baseline 1
round(new_frame_cat13['baseline_last10'].mean(),2)   #Baseline 2-simple Average 
round(new_frame_cat13['baseline_last10_wa_ae'].mean(),2)   #Baseline 2-Weighted Average 


#Saving the dataframe for later use of time weights
new_frame_cat13.to_csv('entire_set.csv') #The column 'w' in this dataframe is used as feature in later models.