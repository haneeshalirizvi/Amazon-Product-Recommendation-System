echo Checking environment...
if not exist "%VENV%" (
    echo Virtual environment not found!
    pause
    exit /b
)
@echo off
setlocal

echo ===============================
echo   Starting Recommendation System
echo ===============================

REM --------- Configuration ---------
set BASE_DIR=D:\i211764_i211723_i212687
set VENV=%BASE_DIR%\myenv
set KAFKA_DIR=%BASE_DIR%\kafka
set PRODUCER=%BASE_DIR%\producer\producer.py
set CONSUMER=%BASE_DIR%\consumer\consumer.py

REM --------- Activate Virtual Env ---------
echo Activating virtual environment...
call %VENV%\Scripts\activate

REM --------- Start Zookeeper ---------
echo Starting Zookeeper...
start "Zookeeper" %KAFKA_DIR%\bin\windows\zookeeper-server-start.bat %KAFKA_DIR%\config\zookeeper.properties

REM Wait for Zookeeper
timeout /t 10 > nul

REM --------- Start Kafka ---------
echo Starting Kafka server...
start "Kafka Server" %KAFKA_DIR%\bin\windows\kafka-server-start.bat %KAFKA_DIR%\config\server.properties

REM Wait for Kafka
timeout /t 10 > nul

REM --------- Start Producer ---------
echo Launching Producer...
start "Producer Service" %VENV%\Scripts\python.exe %PRODUCER%

REM Wait before opening producer UI
timeout /t 5 > nul

echo Opening Producer UI...
start http://127.0.0.1:8080/

REM --------- Start Consumer ---------
echo Launching Consumer...
start "Consumer Service" %VENV%\Scripts\python.exe %CONSUMER%

REM Wait before opening consumer UI
timeout /t 5 > nul

echo Opening Recommendation UI...
start http://127.0.0.1:5000/

echo ===============================
echo   System Started Successfully
echo ===============================

pause