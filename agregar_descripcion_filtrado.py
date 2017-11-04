# -*- coding: utf-8 -*-
# Mike Brian Olivera
import sqlite3

sql = "UPDATE licitaciones SET descripcion_filtrado = ? WHERE id = ?"
con = sqlite3.connect('database.db')
con.text_factory = str
cur = con.cursor()    
cur.execute("SELECT * FROM licitaciones")
rows = cur.fetchall()
for row in rows:
	br = row[4].index("<br/>")+5
	descripcion =  row[4][br:]
	descripcion = descripcion[:descripcion.index("<br />")]
	cur.execute(sql, (descripcion,str(row[0])))
	print row[0]
con.commit()
print "finish"