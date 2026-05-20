# Full Stack Integration

## Runtime Architecture

```text
Browser
  -> Flask routes in codes/Backend/app.py
  -> Frontend templates in codes/Frontend/templates
  -> Static CSS/JS in codes/Frontend/static
  -> MySQL database forensic_medicine_db
```

## Backend Configuration

The backend reads these environment variables:

```text
FORENSIC_DB_ENGINE=mysql
FORENSIC_MYSQL_HOST=127.0.0.1
FORENSIC_MYSQL_PORT=3306
FORENSIC_MYSQL_USER=forensic_user
FORENSIC_MYSQL_PASSWORD=forensic123
FORENSIC_MYSQL_DATABASE=forensic_medicine_db
```

`start.ps1`, `start.bat`, and `start.sh` set these values automatically.

## Database Integration

The Flask backend uses PyMySQL to connect to MySQL. SQL queries are kept in the backend and use parameterized statements. The database itself is created manually from:

```text
data/mysql_forensic_database.sql
```

## Frontend Integration

This project does not need a separate frontend development server. Flask serves:

- HTML pages from `codes/Frontend/templates`
- CSS and JavaScript from `codes/Frontend/static`

That keeps the local demo simple:

```text
Start MySQL -> Start Flask -> Open browser
```
