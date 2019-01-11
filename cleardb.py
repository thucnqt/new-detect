import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="anhthuc1996",
  database="object_detection"
)

mycursor = mydb.cursor()
sql = "truncate detect"

mycursor.execute(sql)
mydb.commit()

