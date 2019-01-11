import sqlalchemy as db
import json
import sys
import sqlalchemy as db
def insert_data(connection, data, table):
    query = db.insert(table).values(data)
    connection.execute(query)
    print "Insert success"

def select_data(connection, table_name):
    query = db.select([table])
    result_Proxy = connection.execute(query)
    result = result_Proxy.fetchall()

database = 'test'
table = 'detect'
user = 'root'
password = 'anhthuc1996'
host = '127.0.0.1'
port = '3306'
connect_db = 'mysql://'+  user + ':' + password + '@'+ host + ':' + port + '/' + database
#print connect_db        
engine = db.create_engine(connect_db)
connection = engine.connect()
metadata = db.MetaData()
table = db.Table(table, metadata, autoload=True, autoload_with=engine)
insert_data(connection, data, table)
