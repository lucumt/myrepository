@echo off
setlocal enabledelayedexpansion
title �����滻�ļ�
rem ͳ���ܹ��滻�˶��ٸ��ļ�
set total=0
rem ������ǰĿ¼�µ������ļ�
for /r %%i in (*.*) do (
   set filename=%%~nxi
   rem ���ļ�������Ҫ��ʱ��Ҫ�����滻
   If NOT "!filename!"=="!filename:sec.m=!" (
      rem ����ļ������ƺ�·����ѭ���ж���ı�����Ҫʹ��!������%�������ֵ
      rem echo %%i -----^> !filename!
      rem ����ļ������ƺ�·����ѭ���ж���ı�����Ҫʹ��!������%�������ֵ
      echo %%i
      rem �ȼ����滻����ļ���
      set fname=!filename!
      set fname=!fname:sec.m=.m! 
      rem Ȼ���ڽ����滻
      ren %%i !fname!
      echo !total! ========��!filename!�滻Ϊ!fname!
      set /a total=!total!+1
      rem ���һ������
      echo. 
   )
)
@echo �ļ��滻��ϣ��ܹ��滻%total%���ļ�!
pause