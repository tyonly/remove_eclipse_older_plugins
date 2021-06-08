# remove_eclipse_older_plugins
Remove eclipse old version plugin in plugins folder 
Usage:
   1) import *plugins.sql* to your test database on your local or remote server
   2) modify *removeChongfuPlugin.py* ,use your database config params.
```
  db_connection = mysql.connector.connect(
          host="*localhost*",
          user="*rent*",
          passwd="*rent*",
          database="*dev_test*"
          )    
```  
  3) copy **removeChongfuPlugin.py** to your plugins folder. Example: *d:\eclipse\plugins*
  4) open command line termianal, run **python removeChongfuPlugin.py**

***
移除elipse插件目录中的旧版本插件
使用方法：
1）导入 *plugins.sql* 到你的本地或者远程测试数据库
2) 修改 *removeChongfuPlugin.py* ，使用你的链接数据库参数
```
  db_connection = mysql.connector.connect(
          host="*localhost*",
          user="*rent*",
          passwd="*rent*",
          database="*dev_test*"
          )    
``` 
3）复制 **removeChongfuPlugin.py** 到你的插件目录。比如：*d:\eclipse\plugins*
4）打开命令行终端 ,运行命令：**python removeChongfuPlugin.py**

***
### **development environment**
VSCODE
PYTHON3
MYSQL5.7

