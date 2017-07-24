#!/usr/bin/env python
import csv
import MySQLdb

mydb = MySQLdb.connect(host='192.168.0.172',
    user='combine',
    passwd='combinegohome',
    db='threatintell')
cursor = mydb.cursor()

csv_data = csv.reader(file('harvest.csv'))
for row in csv_data:
	cursor.execute("INSERT IGNORE INTO ip_reputation(host, type, direction, source_url, tag, date) VALUES(%s, %s, %s, %s, %s, %s)",row)
#close the connection to the database.
mydb.commit()
cursor.close()
print "Done"
