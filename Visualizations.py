import psycopg2 as pg
import pandas as pd
import matplotlib.pyplot as plt
import pandas.io.sql as sqlio
import numpy as np

conn = pg.connect("host=localhost dbname=postgres user=postgres password = Infinity!90")
cur = conn.cursor()

#######################################################################################
####Gather the craetion and resolution dates per month
#######################################################################################
df = pd.read_sql_query('select * from questions where settled_value is not null and type = \'binary\'', conn)
df['daystoresolve'] = (df['settled_at'] - df['created_at']).dt.days

df = df[df['daystoresolve'] > 0]
df = df.reset_index(drop = True)

monthly = df.set_index('created_at').groupby(pd.Grouper(freq='M'))['id'].count()
monthly.index = monthly.index.strftime('%m/%d/%Y')
monthly.plot(kind='bar')
plt.title('Questions created per month', fontsize = 15)
plt.ylabel('Frequency')
plt.show()

monthly_1 = df.set_index('settled_at').groupby(pd.Grouper(freq='M'))['id'].count()

daterange = [monthly.index[0]]
for l in range(0, len(monthly_1)):
    daterange.append(monthly_1.index[l])

monthly_1.index = monthly_1.index.strftime('%m/%d/%Y')
monthly_1.plot(kind='bar')
plt.title('Questions resolved per month', fontsize = 15)
plt.ylabel('Frequency')
plt.show()


###########################################################################################
#Create a dataframe that plot the simple moving average
#######################################################################################

userdata = pd.read_csv("D:\\Fall 2019\\CAP\\weighted avg\\usersBigdata.csv")
#get the settled range 
totalerror = []
movingaverageDF = pd.DataFrame()
for m in range(0, len(daterange)-1):
    query = "select id from questions where settled_value is not null and type = 'binary' and settled_at between '{}' AND '{}'".format(daterange[m], daterange[m+1])
    qids = pd.read_sql_query(query, conn)
    trades = userdata[userdata['question_id'].isin(qids['id'])] 
    totalerror.append(trades['error'].mean())
    
#    #Gets the average error per category 1 and 2
#    errorusers1 = trades.groupby('category1', as_index=False)['error'].mean()#.mean()
#    errorusers2 = trades.groupby('category2', as_index=False)['error'].mean()
#    errorusers2.columns = errorusers1.columns
#    #Combines the error 
#    error = errorusers1.append(errorusers2).reset_index(drop = True)
#    meanerror = error.groupby('category1', as_index = False)['error'].mean()

#Gets the average error per category 1 and 2
    errorusers1 = trades.groupby('category1', as_index=False)['error'].sum()#.mean()
    errorusers1['count'] = trades.groupby('category1', as_index=False)['error'].count()['error']
    errorusers2 = trades.groupby('category2', as_index=False)['error'].sum()
    errorusers2['count'] = trades.groupby('category2', as_index=False)['error'].count()['error']
    errorusers2.columns = errorusers1.columns
    #Combines the error 
    error = errorusers1.append(errorusers2).reset_index(drop = True)
    meanerror = error.groupby('category1', as_index = False).sum()
    meanerror['avgError'] = meanerror['error']/meanerror['count']
    meanerror['Date'] = daterange[m+1]
    
    #Append meanerror for each month to the dataframe created above
    movingaverageDF = movingaverageDF.append(meanerror)


###########################################################################################
#plot the simple moving average
#######################################################################################
##Plot 1 - Cumulative graph


by_label = movingaverageDF.groupby('category1')
plt.figure(figsize=(12,8))
for name, group in by_label:
    plt.plot(group['Date'], group['avgError'], label=name)

plt.legend(loc='upper left')
plt.title("Simple Moving average - Distribution of error per category", fontsize = 20)
plt.xlabel('Time of resolution', fontsize = 15)
plt.ylabel('Average error', fontsize = 15)
plt.xticks(rotation = 75)
plt.show     

###Plot 2 : Individual plots created as list
i = 0 #counter for plot
k = 0
fig, axs = plt.subplots(14, sharex=True, sharey = True, figsize = (8,27))
fig.text(0.5, 0.07, 'Time of resolution', ha='center', fontsize = 15)
fig.text(0.06, 0.5, 'Mean absolute error', va='center', rotation='vertical', fontsize = 15)
for catg in movingaverageDF.category1.unique()[:-1]:
    if(catg != 'IEEE Spectrum'):
        subdf = movingaverageDF[movingaverageDF.category1 == catg]
        #fig.suptitle('Sharing both axes')
        axs[i].plot(subdf['Date'], subdf['avgError'] )
        #axs[i].set_yticklabels(np.arange(0, 1, 0.1)) 
        plt.xticks(rotation = 75, fontsize = 12)
        #plt.yticks(subdf['avgError'], np.arange(0, 1, 0.1))
        i +=1
j =0
for ax in axs:
    ax.label_outer()
    ax.set_title(movingaverageDF.category1.unique()[j])
    j += 1


###Plot 2 : As grid
fig, t= plt.subplots(7, 2,figsize = (8, 12), sharex = True, sharey =True)

fig.text(0.5, 0, 'Time of resolution', ha='center', fontsize = 15)
fig.text(0, 0.5, 'Mean absolute error', va='center', rotation='vertical', fontsize = 15)
a = 0
b = 0
for c,num in zip(movingaverageDF.category1.unique(), range(1,15)):
    df0= movingaverageDF[movingaverageDF.category1 == c]
    ax = t[a, b]
    ax.plot(df0['Date'], df0['avgError'])
    ax.set_title(c) 
    ax.tick_params(labelrotation=55)
    #plt.xticks(rotation = 55)
    if(num % 2 == 0):
        a += 1
        b = 0
    else:
        b += 1

plt.tight_layout()
plt.show()

    


###########################################################################################
# Binary Questions per category plot
###########################################################################################

questpercat = userdata.groupby('category1')['question_id'].nunique().reset_index()
QC = questpercat.question_id.sum()
vallist =[]
for catg in movingaverageDF.category1.unique()[:-1]:
    vallist.append(userdata[userdata.category1 == catg]['question_id'].nunique() + userdata[userdata.category2 == catg]['question_id'].nunique() )

bincat = pd.DataFrame(vallist, index = movingaverageDF.category1.unique()[:-1], columns= ['QuestionsCount'])  
bincat.plot(kind = 'barh') 
plt.title('Number of Binary questions per category',fontsize=15)
plt.show()

###########################################################################################
#VALIDATION -- questions belong to other categories such as study and scicast........
q1 = userdata['question_id'].unique().tolist()
q = df['id']
q[~q.isin(q1)]
q1[~q1.isin(q)]

##############IDK
daterange = []
for l in range(0, len(monthly_1)):
    daterange.append(monthly_1.index[l])

monthdf = pd.DataFrame([[0, '01-01-01', 0]])
for m in range(0, len(daterange)-1):
    for i in range(0, len(df)):
        query = "select user_id, new_value, created_at from historical_trades where question_id = {} and created_at between '{}' AND '{}'".format(df['id'][i], monthly.index[m], monthly_1.index[m])
        #print(query)
        trades_month1 = pd.read_sql_query(query, conn)
        if( len(trades_month1) >0 ):
            monthavg = trades_month1['new_value'].mean()
            newdf = pd.DataFrame([[df['id'][i], daterange[m+1], monthavg]])
            print(newdf)
            monthdf.append(newdf, ignore_index = True)
        

query = "select id, name, created_at, settled_at, settled_value  from questions where settled_value is not null and type = 'binary' and (created_at between '2013-11-30' AND '2014-01-31') and (settled_at between '2013-11-30' AND '2014-02-28')"
questions_month1 = pd.read_sql_query(query, conn)
questions_month1['daystoresolve'] = (questions_month1['settled_at'] - questions_month1['created_at']).dt.days
questions_month1 = questions_month1[questions_month1['daystoresolve'] > 0]

monthavg = []
for i in range(0, len(questions_month1)):
    query = "select user_id, new_value, created_at from historical_trades where question_id = {} order by created_at".format(questions_month1['id'][i])
    trades_month1 = pd.read_sql_query(query, conn)
    monthavg.append((trades_month1['new_value']).mean())

questions_month1['predictions'] = monthavg