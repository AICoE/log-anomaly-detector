# Fact Store 

## Overview

In this repository we are experimenting with building a user feedback driven fact store.
 This will be a service that will utilized to query for finding false predictions. 
 Also will allow users to click which anomaly is not really an anomaly for example.

![](./imgs/design.jpg) 

## Database

Metadata such as events and feedback are stored in a database. We are using sqlalchemy
and by default it will autocreate your tables and provide you a sqlite datatabase.
If you would like to utilize a different storage database that is supported 
by sqlalchemy then you can visit the following link. 

See: https://docs.sqlalchemy.org/en/latest/dialects/


You would provide a connection string for example if your using mysql:

To test this locally try:
```bash
export SQL_CONNECT="mysql+pymysql://{USERNAME}:{PASSWORD}@localhost/factstore"
python app.py ui --port 8080 --debug True

```

### Deploy mysql test instance on openshift:
```bash
oc new-app \
    -e MYSQL_USER=<USER> \
    -e MYSQL_PASSWORD=<MYSQL_PASSWORD> \
    -e MYSQL_ROOT_PASSWORD=<MYSQL_ROOT_PASSWORD> \
    -e MYSQL_DATABASE=<MYSQL_DATABASE> \
    openshift/mysql-56-centos7
    
 oc rsh <pod>
 
 
 mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $HOSTNAME $MYSQL_DATABASE
 

mysql>

```

### MYSQL Creating schema and user
```sql

CREATE USER 'USERNAME'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON * . * TO 'USERNAME'@'localhost';
CREATE SCHEMA `factstore` ;

```
Note: Replace USERNAME with the user you would like to use for the factstore.

### OpenShift deployment:
Execute the following command to deploy the fact_store to openshift via s2i
```bash
oc new-app python~https://github.com/AICoE/log-anomaly-detector.git -e PYTHONPATH='/opt/app-root/src'  -e APP_FILE='fact_store/app.py' --name='factstore-zmhassan' 
oc expose svc/factstore-zmhassan 
oc logs -f bc/factstore-zmhassan
```


### Status

This is in development and not ready for use yet.
