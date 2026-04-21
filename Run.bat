@echo off
setlocal
echo Starting ENV.

echo REM SET the virtual environment
set VIRTUAL_ENV=D:\i211764_i211723_i212687\myenv

echo REM Activate the virtual environment
call %VIRTUAL_ENV%\Scripts\activate

echo REM Start Zookeeper
start "Start Kafka" D:\i211764_i211723_i212687\kafka\bin\windows\zookeeper-server-start.bat D:\i211764_i211723_i212687\kafka\config\zookeeper.properties
ping 127.0.0.1 -n 20 > nul
echo  Start Kafka
start "Start Kafka" D:\i211764_i211723_i212687\kafka\bin\windows\kafka-server-start.bat D:\i211764_i211723_i212687\kafka\config\server.properties

echo Wait for Kafka to start with Zookeeper
ping 127.0.0.1 -n 10 > nul


echo Start your producer file
start "Start producer" D:\i211764_i211723_i212687\myenv\Scripts\python.exe D:\i211764_i211723_i212687\producer\producer.py
ping 127.0.0.1 -n 5 > nul

echo Wait for the Flask server of Producer
start "Wait for the Flask server of Producer" http://127.0.0.1:8080/
ping 127.0.0.1 -n 20 > nul
echo Start consumer
start "Start consumer" D:\i211764_i211723_i212687\myenv\Scripts\python.exe D:\i211764_i211723_i212687\consumer\consumer.py

ping 127.0.0.1 -n 8 > nul
echo Open the browser to localhost:5000 of Consumer
start "Open the browser to localhost:5000 of Consumer" http://127.0.0.1:5000/
