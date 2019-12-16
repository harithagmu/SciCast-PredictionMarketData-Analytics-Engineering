import psycopg2 as pg
import pandas as pd

conn = pg.connect("")
cur = conn.cursor()

df = pd.read_sql_query("select id, settled_value from questions where type = 'binary' and settled_value is not NULL", conn)
#df = questions.head(4)

errorlist = []
for i in range(0, len(df)):
    query = "select user_id, new_value from historical_trades where question_id = {} and user_id <> 1 order by created_at desc LIMIT 1".format(df['id'][i])
    trades = pd.read_sql_query(query, conn)
    if(len(trades) > 0):
        error = abs(trades['new_value'][0]- df['settled_value'][i])        
    else:
        error = 'NA'
    errorlist.append(error)
df['absError'] = errorlist    
df.to_csv("D:\\Fall 2019\\CAP\\weighted avg\\basline.csv")   
    
#Questions where only admin made trade
#960, 955,1297,980,1266,950,1303,1375,166,780,1217,985,976,970,945,852,810,340,567,1218,990,367,870,881,619,463,1125,1211,1212,308,412,1079,784,550,1105,676,270,368


