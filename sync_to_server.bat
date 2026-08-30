@echo off
title JX1 Server Sync Tool - Windows to Linux VM
chcp 65001 >nul
color 0A

set "SRC=%~dp0"
if "%SRC:~-1%"=="\" set "SRC=%SRC:~0,-1%"
set "DST=\\192.168.1.188\jxser\server1"

:: Danh sach thu muc bo qua (khong can copy)
set "EXCLUDE_DIRS=.git .agents .brain Logs dulieu itemexchange_setting rolevalueladder_setting worldrank font servershutdown_log pak data"

:: Danh sach file bo qua
set "EXCLUDE_FILES=*.tmp *.log sync_to_server.bat *.py *.bak 192.168.1.188"

:menu
cls
echo ===================================================================
echo             CONG CU DONG BO VO LAM SIM -^> LINUX SERVER
echo ===================================================================
echo   [Nguon] : %SRC%
echo   [Dich]  : %DST%
echo ===================================================================
echo.
echo   [1] Dong bo 1 lan duy nhat roi dong (Sync Once) - Khuyen dung
echo   [2] Tu dong dong bo lien tuc moi 5s (Auto-Sync Realtime)
echo   [0] Thoat
echo.
echo ===================================================================
set /p opt="Hay chon che do (mac dinh [1]): "

if "%opt%"=="" set opt=1
if "%opt%"=="1" goto sync_once
if "%opt%"=="2" goto sync_loop
if "%opt%"=="0" exit /b
goto menu

:sync_once
cls
echo ===================================================================
echo   DANG DONG BO 1 LAN SANG LINUX SERVER...
echo ===================================================================
echo.

robocopy "%SRC%" "%DST%" /E /XO /FFT /R:1 /W:1 /MT:8 /XD %EXCLUDE_DIRS% /XF %EXCLUDE_FILES% /NDL /nc /ns /np

echo.
echo ===================================================================
echo   [OK] DA DONG BO HOAN TAT SANG MAY CHU LINUX!
echo ===================================================================
echo.
echo Nhan phim bat ky de thoat...
pause >nul
exit /b

:sync_loop
cls
echo ===================================================================
echo   CHE DO TU DONG THEO DOI (AUTO-SYNC REALTIME MOI 5 GIAY)
echo   Nhan Ctrl + C hoac dong cua so de dung.
echo ===================================================================
echo.
echo [*] Dang lang nghe thay doi file script/code...
echo.

:loop_start
robocopy "%SRC%" "%DST%" /E /XO /FFT /R:1 /W:1 /MT:8 /XD %EXCLUDE_DIRS% /XF %EXCLUDE_FILES% /NJH /NJS /NDL /nc /ns /np

timeout /t 5 /nobreak >nul
goto loop_start
