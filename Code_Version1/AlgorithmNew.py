import psycopg2 as pg
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
import matplotlib.pyplot as plt

conn = pg.connect("host=localhost dbname=postgres user=postgres password = Infinity!90")
cur = conn.cursor()

#Gather question for training weights for
query = "select created_at, settled_at, settled_value  from questions "
ref = pd.read_sql_query(query, conn)
query = "select id, name, created_at, settled_at, settled_value  from questions where settled_value is not null and type = 'binary'"
questions_month1 = pd.read_sql_query(query, conn)
questions_month1['daystoresolve'] = (questions_month1['settled_at'] - questions_month1['created_at']).dt.days
questions_month1 = questions_month1[questions_month1['daystoresolve'] > 0]

#gather question categories
query = "select question_id, category_id from question_category_links"
questions_categories = pd.read_sql_query(query, conn)
query = "select id, name from question_categories where question_categories.desc is NULL"
categories_names = pd.read_sql_query(query, conn)

#toget the categories based on above 3 tables
#questions_categories[questions_categories['question_id'] == questions_month1]
#categories_names[categories_names['id'].str[0] == ]

#########
#create table trades as (select h.user_id, h.question_id, h.created_at, h.updated_at, h.new_value from historical_trades h join 
#questions q on q.id = h.question_id where q.type = 'binary' and q.settled_value is not null)
#########
#Gather users for look up table
#query = "select distinct user_id from historical_trades where question_id in (select id from questions where type = 'binary' and settled_value is not null and (created_at between '2013-10-30' AND '2014-11-30') and (settled_at between '2013-10-30' AND '2014-11-30'))"#) and (created_at between '2013-11-30' AND '2014-05-30')"
query = "select distinct user_id from historical_trades where question_id in (select id from questions where type = 'binary' and settled_value is not null)"
binaryusers = sqlio.read_sql_query(query, conn)

##This is for testing above query validity
#qidstrlist = ''
#for val in questions_month1['id'].values:
#    qidstrlist += str(val) + ','
#
#query = 'select distinct user_id from historical_trades where question_id in ({})'.format(qidstrlist[:-1])
#TUI = sqlio.read_sql_query(query, conn)


query = "select v.user_id from validuserids v left join historical_trades h on v.user_id = h.user_id"
validuser_madetrades = sqlio.read_sql_query(query, conn)

binarytraders = [x for x in binaryusers['user_id'] if x in validuser_madetrades['user_id']]
binarytraders.sort()

#Gather categories for lookup table
query = "SELECT name FROM question_categories where question_categories.desc is NULL"
categories = sqlio.read_sql_query(query, conn)

#Initialize lookup table
lookupdf = pd.DataFrame(1/(len(binarytraders)), index = binarytraders, columns = categories['name'])
usersBigdata = pd.DataFrame()

#Remove user id =1 
binarytraders.remove(1)
questions_month1.reset_index(drop = True)#.head(15)
categories_names.reset_index(drop = True)#

#Process the weights
for uid in binarytraders:
    actualValue = []
    category1 = []
    category2 = []
    delqids = []
    query = "select user_id, question_id, new_value, created_at from historical_trades where user_id = {} order by created_at".format(uid)
    trades_user = pd.read_sql_query(query, conn)
    
    if(len(trades_user) > 0):
        trades_user = trades_user.loc[trades_user['question_id'].isin(questions_month1['id'] )]
        
    if(len(trades_user) > 0): #Need to check again 
         #Delete the duplicate records for the same question --> only last trade of the user for a  question is considered
        s = trades_user[trades_user.duplicated(subset='question_id',keep='last')]
        trades_user.drop(s.index, inplace=True)
        trades_user = trades_user.reset_index(drop = True)
        #Add categories column and settled value column
    
        for qid in trades_user['question_id']:            
            catid = questions_categories[questions_categories['question_id'] == qid]['category_id']
            if(len(catid)):                
                category1_name = categories_names[categories_names['id'] == catid[catid.index[0]]]['name']
                if(len(category1_name) > 0):
                    actualValue.append(questions_month1[questions_month1['id'] == qid]['settled_value'].item()) 
                    category1.append(category1_name.item())
                else:
                    delqids.append(qid)
                    continue #When a question comes from categories other than the above 14, skip that question
                if(len(catid) > 1):
                    category2_name = categories_names[categories_names['id'] == catid[catid.index[1]]]['name']
                    if(len(category2_name) > 0):
                        category2.append(category2_name.item())
                    else:
                        category2.append("")
                else:
                    category2.append("")
            else:
                #Invalid question. qid = 1
                delqids.append(qid)
                
        trades_user= trades_user[~trades_user['question_id'].isin(delqids)]
        trades_user['category1'] = category1
        trades_user['category2'] = category2
        trades_user['actual_Value'] = actualValue
        trades_user['error'] = abs(trades_user['actual_Value'] - trades_user['new_value'])
        
        usersBigdata = usersBigdata.append(trades_user)   
        
        #Aggregate the weights per category1 and 2
        trades_user['category2'] = trades_user['category2'].replace('', np.nan, regex=True)
        cat1 = trades_user.groupby('category1')['error'].apply(lambda x: x.mean(skipna=False))#trades_user.groupby('category1', as_index=False)['error'].mean()
        cat2 = trades_user.groupby('category2')['error'].apply(lambda x: x.mean(skipna=False))
        
        for c1 in range(0, len(cat1)):
             lookupdf[cat1.index[c1]][uid] = cat1.values[c1]
        for c2 in range(0, len(cat2)):
             lookupdf[cat2.index[c2]] [uid]= cat2.values[c2]
       
#The reason why the common weight should be = 1/ total number of users instead of 1/users who made trades in that category        
cat1users = usersBigdata.groupby('category1', as_index=False)['user_id'].count()#.mean()
cat2users = usersBigdata.groupby('category2', as_index=False)['user_id'].count()
usercount = cat1users.append(cat2users).reset_index(drop = True)

users = usercount.groupby('category1', as_index = False)['user_id'].sum()
users = users[users['category1'] != ''].reset_index(drop = True)
users.plot(kind = 'barh', legend = False)
plt.yticks(np.arange(len(users)), users['category1'])
plt.title('Number of participants per category',fontsize=15)
plt.show()



     
usersBigdata.to_csv("D:\\Fall 2019\\CAP\\weighted avg\\usersBigdata.csv")         
lookupdf.to_csv("D:\\Fall 2019\\CAP\\weighted avg\\lookup.csv")
     
