@echo off
setlocal enabledelayedexpansion
title 批量替换文件
rem 统计总共替换了多少个文件
set total=0
rem 遍历当前目录下的所有文件
for /r %%i in (*.*) do (
   set filename=%%~nxi
   rem 当文件名符合要求时，要进行替换
   If NOT "!filename!"=="!filename:sec.m=!" (
      rem 输出文件的名称和路径，循环中定义的变量需要使用!而不是%来输出其值
      rem echo %%i -----^> !filename!
      rem 输出文件的名称和路径，循环中定义的变量需要使用!而不是%来输出其值
      echo %%i
      rem 先计算替换后的文件名
      set fname=!filename!
      set fname=!fname:sec.m=.m! 
      rem 然后在进行替换
      ren %%i !fname!
      echo !total! ========将!filename!替换为!fname!
      set /a total=!total!+1
      rem 输出一个空行
      echo. 
   )
)
@echo 文件替换完毕，总共替换%total%个文件!
pause