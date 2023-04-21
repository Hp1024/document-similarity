import sys,os
import cx_Oracle
con=cx_Oracle.connect('scott/tiger@127.0.0.1/XE')
cus=con.cursor()
cus.execute('select distinct document from search')
y=fetchall()
path=input('ENTER THE PATH : ')
for x in y:
    print(x)
    for x not in os.listdir(path):
        print(x)
