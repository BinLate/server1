@echo off
title JX1 Server Sync Tool - Windows to Linux VM
chcp 65001 >nul
color 0A

set "SRC=%~dp0"
if "%SRC:~-1%"=="\" set "SRC=%SRC:~0,-1%"
set "DST=\\192.168.1.188\jxser\server1"

:: Danh sach thu muc bo qua (khong sync sang game server)
:: - Dev/agent: .git .agents .ai .brain .pytest_cache plans tests tools scripts
:: - Runtime local / binary da co san tren Linux: Logs dulieu pak data font ...
set "EXCLUDE_DIRS=.git .agents .ai .brain .pytest_cache .github __pycache__ plans tests tools scripts gemini-and-chatgpt upstream_simcity Logs dulieu itemexchange_setting rolevalueladder_setting worldrank font servershutdown_log pak data"

:: Danh sach file bo qua
set "EXCLUDE_FILES=*.tmp *.log *.py *.pyc *.bak *.md *.pdf .gitignore sync_to_server.bat 192.168.1.188 requirements-test.txt checks.json chatgpt_response_*.txt AGENTS.md CHANGELOG.md PROJECT_MAP.md"

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
