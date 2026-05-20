#!/usr/bin/env sh
export FORENSIC_DB_ENGINE=mysql
export FORENSIC_MYSQL_HOST=127.0.0.1
export FORENSIC_MYSQL_PORT=3306
export FORENSIC_MYSQL_USER=forensic_user
export FORENSIC_MYSQL_PASSWORD=forensic123
export FORENSIC_MYSQL_DATABASE=forensic_medicine_db
python codes/Backend/run_server.py
