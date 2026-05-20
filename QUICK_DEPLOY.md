# Quick Deploy Locally

## 1. Start MySQL

```powershell
net start MySQL80
```

If your service name is different, open Windows Services and start the MySQL service from there.

## 2. Create Database

Open MySQL Workbench or MySQL CLI and run:

```text
X:\Forensic\data\mysql_forensic_database.sql
```

## 3. Install Python Packages

```powershell
cd X:\Forensic
python -m pip install -r codes\Backend\requirements.txt
```

## 4. Start App

```powershell
cd X:\Forensic
.\start.ps1
```

## 5. Open Browser

```text
http://127.0.0.1:5000/login
```

Login:

```text
admin / admin123
```
