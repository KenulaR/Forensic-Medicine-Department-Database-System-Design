$env:FORENSIC_DB_ENGINE = "mysql"
$env:FORENSIC_MYSQL_HOST = "127.0.0.1"
$env:FORENSIC_MYSQL_PORT = "3306"
$env:FORENSIC_MYSQL_USER = "forensic_user"
$env:FORENSIC_MYSQL_PASSWORD = "forensic123"
$env:FORENSIC_MYSQL_DATABASE = "forensic_medicine_db"
Remove-Item Env:\SSLKEYLOGFILE -ErrorAction SilentlyContinue

python codes\Backend\run_server.py
