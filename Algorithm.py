import psycopg2 as pg
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np

conn = pg.connect("host=localhost dbname=postgres user=postgres password = Infinity!90")
cur = conn.cursor()

df = pd.read_sql_query('select * from questions where settled_value is not null and type = \'binary\'', conn)
df['daystoresolve'] = (df['settled_at'] - df['created_at']).dt.days

df['id'].plot(linewidth=0.5)

#Exclude the rows thatb have daystoresolve = 0
df = df[df['daystoresolve'] > 0]

#Visualization for number of questions created and 
monthly = df.set_index('created_at').groupby(pd.Grouper(freq='M'))['id'].count()
monthly.plot(kind='bar')
monthly_1 = df.set_index('settled_at').groupby(pd.Grouper(freq='M'))['id'].count()
monthly_1.plot(kind='bar')

#Visualization for questions against resolution days
df['daystoresolve'].plot(linewidth = 1)

#Gather users for look up table
query = "select distinct user_id from historical_trades where question_id in (select id from questions where type = 'binary' and settled_value is not null) "
binaryusers = sqlio.read_sql_query(query, conn)

query = "select v.user_id from validuserids v left join historical_trades h on v.user_id = h.user_id"
validuser_madetrades = sqlio.read_sql_query(query, conn)

binarytraders = [x for x in binaryusers['user_id'] if x in validuser_madetrades['user_id']]
binarytraders.sort()
#Ignore first user
binarytraders = binarytraders[1:]
#Gather categories for lookup table
query = "SELECT name FROM question_categories where question_categories.desc is NULL"
categories = sqlio.read_sql_query(query, conn)
#Create a look up table
#colsnames = [x for x in validuser_madetrades['user_id'] if x != 1]
#colsnames.sort()
lookupdf = pd.DataFrame(1/(len(binarytraders)), index = categories['name'], columns = binarytraders)

'''
2 Month analysis
'''
#Created in the first 2 months and resolved in the next 2 months
query = "select id, name, created_at, settled_at, settled_value  from questions where settled_value is not null and type = 'binary' and (created_at between '2013-11-30' AND '2014-01-31') and (settled_at between '2013-11-30' AND '2014-02-28')"
questions_month1 = pd.read_sql_query(query, conn)
questions_month1['daystoresolve'] = (questions_month1['settled_at'] - questions_month1['created_at']).dt.days
questions_month1 = questions_month1[questions_month1['daystoresolve'] > 0]
#Get the categories of both questions
catgry1 = []
catgry2 = []
for i in range(0, len(questions_month1)):
    #cur.execute('rollback')
    q = "SELECT name FROM question_categories C JOIN question_category_links L on L.category_id = C.id where L.question_id = {}".format(questions_month1['id'][i])
    dat = sqlio.read_sql_query(q, conn)
    catgry1.append(dat.name[0])
    if len(dat) >0:
        catgry2.append(dat.name[1])
    else:
        catgry2.append("")
questions_month1['category1'] = catgry1
questions_month1['category2'] = catgry2

for i in range(0, len(questions_month1)):
    query = "select user_id, new_value, created_at from historical_trades where question_id = {} order by created_at".format(questions_month1['id'][0])
    trades_month1 = pd.read_sql_query(query, conn)
    
    #Delete the duplicate records for the same user --> only last trade of the user for a  question is considered
    s = trades_month1[trades_month1.duplicated(subset='user_id',keep='last')]
    trades_month1.drop(s.index, inplace=True)
    trades_month1 = trades_month1.reset_index(drop = True)
    
    #base model - mean absolute error
    baseError = abs(questions_month1['settled_value'][0] - trades_month1['new_value'].tail(1))
    
    #GH: May be get the value and add to it -- done , discuss
    #GH: Need to figure out a min and max value so that the weights dont go negative or too huge
    #update initial weights for users -- start of month
    initwt = 1/len(trades_month1['user_id'])
    for t in trades_month1['user_id']:
        lookupdf[t][questions_month1['category1'][0]] = lookupdf.loc[questions_month1['category1'][0], t] + initwt
        if questions_month1['category2'][0] != "":
            lookupdf[t][questions_month1['category2'][0]] = lookupdf.loc[questions_month1['category2'][0], t] + initwt
    
    #Increase or decrease weights -- end of month
    #get absolute error for each user
    trades_month1['error'] = abs(questions_month1['settled_value'][0] - trades_month1['new_value'])
    #Loop through each user trades, find the weight and update lookup table
    for j in range(0, len(trades_month1)):
        error = trades_month1['error'][j] 
        if(error > 0.6): # reduce
            updatewt = (initwt * error)/15 #Dividing by 15 in order to get a much smaller change in the weight
            lookupdf[trades_month1['user_id'][j]][questions_month1['category1'][0]] = lookupdf.loc[questions_month1['category1'][0], trades_month1['user_id'][j]] - updatewt
            if questions_month1['category2'][0] != "":
                lookupdf[trades_month1['user_id'][j]][questions_month1['category2'][0]] = lookupdf.loc[questions_month1['category2'][0], trades_month1['user_id'][j]] - updatewt
        #else if error <= 0.6 and error >= 0.5:
         #   print("No increase nor decrease")
        elif error < 0.4: #increase
            updatewt = (initwt * (0.4-error))/15 #0.4-error because more weights should be added if the error rate is low
            lookupdf[trades_month1['user_id'][j]][questions_month1['category1'][0]] = lookupdf.loc[questions_month1['category1'][0], trades_month1['user_id'][j]] + updatewt
            if questions_month1['category2'][0] != "":
                lookupdf[trades_month1['user_id'][j]][questions_month1['category2'][0]] = lookupdf.loc[questions_month1['category2'][0], trades_month1['user_id'][j]] + updatewt

            
    
        
        
        
        
        
        
    
    




