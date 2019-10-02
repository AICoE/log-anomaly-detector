Fact Store
==========

Overview
--------
In this repository we are experimenting with building a user feedback driven fact store. This will be a service that will utilized to query for finding false predictions. Also will allow users to click which anomaly is not really an anomaly for example.



Database
--------
Metadata such as events and feedback are stored in a database. We are using sqlalchemy and by default it will autocreate your tables and provide you a sqlite datatabase. If you would like to utilize a different storage database that is supported by sqlalchemy then you can visit the following link.

See: https://docs.sqlalchemy.org/en/latest/dialects/

You would provide a connection string for example if your using mysql:


Deploy mysql test instance on openshift:


.. code-block:: shell

    oc new-app \
    -e MYSQL_USER=<USER> \
    -e MYSQL_PASSWORD=<MYSQL_PASSWORD> \
    -e MYSQL_ROOT_PASSWORD=<MYSQL_ROOT_PASSWORD> \
    -e MYSQL_DATABASE=<MYSQL_DATABASE> \
    openshift/mysql-56-centos7

    oc rsh <pod>


    mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $HOSTNAME $MYSQL_DATABASE



    mysql>


MSQL Create User
----------------
.. code-block:: sql


    CREATE USER 'USERNAME'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON * . * TO 'USERNAME'@'localhost';
    CREATE SCHEMA `factstore` ;


.. note::

   Replace USERNAME with the user you would like to use for the factstore.



