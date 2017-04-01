SET NGINX_PATH=D:
SET NGINX_DIR=D:\web\nginx-1.4.2\
SET PHP_DIR=D:\web\php\php-5.3.27\
++++++++++++++++++代码开始++++++++++++++++
cls
@ECHO OFF
SET NGINX_PATH=D:
SET NGINX_DIR=D:\web\nginx-1.4.2\
SET PHP_DIR=D:\web\php\php-5.3.27\
color 0a
TITLE Nginx+PHP 管理程序(飞狐 http://lucumt.info)
GOTO MENU
:MENU
CLS
ECHO.
ECHO. * * * * * * * Nginx+PHP 管理程序 * * * * * *
ECHO. * *
ECHO. * 1 启动Nginx *
ECHO. * *
ECHO. * 2 关闭Nginx *
ECHO. * *
ECHO. * 3 重启Nginx *
ECHO. * *
ECHO. * 4 启动php-cgi *
ECHO. * *
ECHO. * 5 关闭php-cgi *
ECHO. * *
ECHO. * 6 重启php-cgi *
ECHO. * *
ECHO. * 7 退 出 *
ECHO. * *
ECHO. * * * * * * * * * * * * * * * * * * * * * * * *
ECHO.
ECHO.请输入选择项目的序号：
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
ECHO.启动Nginx......
IF NOT EXIST %NGINX_DIR%nginx.exe ECHO %NGINX_DIR%nginx.exe不存在
%NGINX_PATH%
cd %NGINX_DIR%
IF EXIST %NGINX_DIR%nginx.exe start %NGINX_DIR%nginx.exe
ECHO.OK
PAUSE
GOTO MENU
:cmd2
ECHO.
ECHO.关闭Nginx......
taskkill /F /IM nginx.exe > nul
ECHO.OK
PAUSE
GOTO MENU
:cmd3
ECHO.
ECHO.关闭Nginx......
taskkill /F /IM nginx.exe > nul
ECHO.OK
GOTO cmd1
GOTO MENU
:cmd4
ECHO.
ECHO.启动php-cgi......
IF NOT EXIST %PHP_DIR%php-cgi.exe ECHO %PHP_DIR%php-cgi.exe不存在
echo set wscriptObj = CreateObject("Wscript.Shell") >start_fastcgi.vbs
echo wscriptObj.run "%PHP_DIR%php-cgi.exe -b 127.0.0.1:9000",0 >>start_fastcgi.vbs
start_fastcgi.vbs
del start_fastcgi.vbs
ECHO.OK
PAUSE
GOTO MENU
:cmd5
ECHO.
ECHO.关闭php-cgi......
taskkill /F /IM php-cgi.exe > nul
ECHO.OK
PAUSE
GOTO MENU
:cmd6
ECHO.
ECHO.关闭php-cgi......
taskkill /F /IM php-cgi.exe > nul
ECHO.OK
GOTO cmd4
GOTO MENU