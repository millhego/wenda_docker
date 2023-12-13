@echo off
chcp 65001
title 闻达
reg add HKEY_CURRENT_USER\Console /v QuickEdit /t REG_DWORD /d 00000000 /f
rem 关闭快速编辑模式，防止大神暂停了还说程序有bug
cls


call :searchFiles "." "python.exe"
IF defined PYTHON ( goto end )
call :searchFiles ".." "python.exe"
IF defined PYTHON ( goto end )

IF EXIST python (
echo 未检测到集成环境，使用系统Python解释器
set "PYTHON=python.exe "
goto end
)
ELSE
(
    echo 未检测到集成环境,请安装Python
)
goto end

:searchFiles
set "search_dir=%1"
set "target=%2"
rem 在项目目录下搜索 python.exe
set "search_file="
for /r "%search_dir%" %%i in (*%target%*) do (
    set "WINPYDIR=%%~dpi"
    set "PATH=%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts;%PATH%;"
    set "PYTHON=%%i"
    echo 找到python环境: %%i
    goto end
)
exit


:end