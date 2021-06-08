#!/usr/bin/python
# -*- coding: UTF-8 -*-

import mysql.connector
import re
import shutil
import pdb
import os

db_connection = mysql.connector.connect(
  	host="localhost",
  	user="rent",
  	passwd="rent",
    database="dev_test"
    )
db_cursor = db_connection.cursor()
sql="TRUNCATE table `plugins`"
db_cursor.execute(sql)

#print(os.getcwd())
current_path = os.path.dirname(__file__)

#uPath = unicode(cPath,'utf-8')
dirs = os.listdir( current_path )
i=0

for file in dirs:
    file_path = os.path.join(current_path, file)
    file_type=1
    v_index = 0
    ver=''
    ver_1 = ''
    ver_arr=''
    min_ver=''
    other_ver=''
    real_name=''
    file_name = file
    if os.path.isdir(file_path):
        file_type=0
    if file_type==1 and file.endswith(".jar"):
        file_name = file.rstrip(".jar")
        
    if file_name.rfind('_')>0:
        index = file_name.rfind('_')
        real_name = file_name[0:index]
        ver = file_name[index+1:]
        ver_1 = ver
        if(ver.rfind('.v')>0):
            v_index = ver.find('.v')
            ver_1 = ver.split('.v')[0]
            ver_arr = ver.split('.v')[1]
            if(ver_arr.find('-')>0):
                min_ver = ver_arr.split('-')[0]
                other_ver=ver_arr.split('-')[1]
            else:
                min_ver = ver_arr
                
    sql = "INSERT INTO `plugins`(`file_name`,`type`,`name`,ver,min_ver,other_ver) VALUES('"+file+"',"+str(file_type)+",'"+real_name+"','"+ver_1+"','"+min_ver+"','"+other_ver+"')"

#    print(sql)
#    pdb.set_trace()
    db_cursor.execute(sql)       
    db_connection.commit()    

#    print(db_cursor.rowcount, "记录插入成功。")        
    i= i+1
#print(i, "条记录插入成功。")    

# del older plugins
sql1="select id,file_name,`name`,ver,SUBSTRING_INDEX( `ver` , '.', 1 )*1 as v1,SUBSTRING_INDEX(SUBSTRING_INDEX( `ver` , '.', 2 ),'.',-1)*1 v2,SUBSTRING_INDEX(SUBSTRING_INDEX( `ver` , '.', 3 ),'.',-1)*1 v3,SUBSTRING_INDEX(SUBSTRING_INDEX( `ver` , '.', 4 ),'.',-1)*1 v4 from `plugins`"
sql2="select t.* from ("+sql1+") t inner join (select `name` from `plugins` where LENGTH(name)>0 GROUP BY `name` HAVING count(*)>1) t2 on t.name = t2.`name` order by t.`name`,t.v1 desc,t.v2 desc,t.v3 desc,t.v4 desc"
sql3="select * from ("+sql2+") t0 GROUP BY t0.`name`"
sql4="select p.id from ("+sql3+") tt INNER JOIN `plugins` p on tt.id=p.id"
sql5="update `plugins` pp INNER JOIN ("+sql2+") p0 on pp.id=p0.id set pp.need_del=1 where LENGTH(pp.`name`)>0 AND pp.id not in (select id from ("+sql4+") a)";
#print(sql5)
db_cursor.execute(sql5)       
db_connection.commit()    
print("UPDATE DEL STATUS SUCCESSFUL!")

# del older plugins file
sql="select * from `plugins` where need_del=1 order by `name`"
db_cursor.execute(sql)
myresult = db_cursor.fetchall()     
for x in myresult:
#    print(x)
    file_name = x[1]
    file_type = x[2]
    file_path = os.path.join(current_path, file_name)
    if file_type==1:
        if os.path.exists(file_path):
          os.remove(file_path)
        else:
          print("The file does not exist")
    else:
        shutil.rmtree(file_path)
   