SET NGINX_PATH=D:
SET NGINX_DIR=D:\web\nginx-1.4.2\
SET PHP_DIR=D:\web\php\php-5.3.27\
++++++++++++++++++���뿪ʼ++++++++++++++++
cls
@ECHO OFF
SET NGINX_PATH=D:
SET NGINX_DIR=D:\web\nginx-1.4.2\
SET PHP_DIR=D:\web\php\php-5.3.27\
color 0a
TITLE Nginx+PHP �������(�ɺ� http://lucumt.info)
GOTO MENU
:MENU
CLS
ECHO.
ECHO. * * * * * * * Nginx+PHP ������� * * * * * *
ECHO. * *
ECHO. * 1 ����Nginx *
ECHO. * *
ECHO. * 2 �ر�Nginx *
ECHO. * *
ECHO. * 3 ����Nginx *
ECHO. * *
ECHO. * 4 ����php-cgi *
ECHO. * *
ECHO. * 5 �ر�php-cgi *
ECHO. * *
ECHO. * 6 ����php-cgi *
ECHO. * *
ECHO. * 7 �� �� *
ECHO. * *
ECHO. * * * * * * * * * * * * * * * * * * * * * * * *
ECHO.
ECHO.������ѡ����Ŀ����ţ�
set /p ID=
IF "%id%"=="1" GOTO cmd1
IF "%id%"=="2" GOTO cmd2
IF "%id%"=="3" GOTO cmd3
IF "%id%"=="4" GOTO cmd4
IF "%id%"=="5" GOTO cmd5
IF "%id%"=="6" GOTO cmd6
IF "%id%"=="7" EXIT
PAUSE
:cmd1
ECHO.
ECHO.����Nginx......
IF NOT EXIST %NGINX_DIR%nginx.exe ECHO %NGINX_DIR%nginx.exe������
%NGINX_PATH%
cd %NGINX_DIR%
IF EXIST %NGINX_DIR%nginx.exe start %NGINX_DIR%nginx.exe
ECHO.OK
PAUSE
GOTO MENU
:cmd2
ECHO.
ECHO.�ر�Nginx......
taskkill /F /IM nginx.exe > nul
ECHO.OK
PAUSE
GOTO MENU
:cmd3
ECHO.
ECHO.�ر�Nginx......
taskkill /F /IM nginx.exe > nul
ECHO.OK
GOTO cmd1
GOTO MENU
:cmd4
ECHO.
ECHO.����php-cgi......
IF NOT EXIST %PHP_DIR%php-cgi.exe ECHO %PHP_DIR%php-cgi.exe������
echo set wscriptObj = CreateObject("Wscript.Shell") >start_fastcgi.vbs
echo wscriptObj.run "%PHP_DIR%php-cgi.exe -b 127.0.0.1:9000",0 >>start_fastcgi.vbs
start_fastcgi.vbs
del start_fastcgi.vbs
ECHO.OK
PAUSE
GOTO MENU
:cmd5
ECHO.
ECHO.�ر�php-cgi......
taskkill /F /IM php-cgi.exe > nul
ECHO.OK
PAUSE
GOTO MENU
:cmd6
ECHO.
ECHO.�ر�php-cgi......
taskkill /F /IM php-cgi.exe > nul
ECHO.OK
GOTO cmd4
GOTO MENU