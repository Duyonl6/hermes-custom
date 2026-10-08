@echo off
chcp 65001 >nul
REM Chạy Tiệm nhà Cam trên Windows: bấm đúp file này. Lần đầu sẽ tự tạo .venv và cài thư viện.
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY goto nopython

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Tao moi truong ao .venv ...
  %PY% -m venv .venv || goto nopython
)
echo [2/3] Cai thu vien (lan dau mat 1-2 phut) ...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt || goto pipfail

echo [3/3] Dang chay: http://localhost:8010   (dong cua so nay de tat)
start "" cmd /c "timeout /t 4 >nul & start http://localhost:8010"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8010
echo.
echo Server da dung. Neu bao loi "address already in use" thi cong 8010 dang bi chuong trinh khac dung.
pause
goto :eof

:nopython
echo Chua tim thay Python 3.10+. Tai tai https://www.python.org/downloads/ va tick "Add python.exe to PATH" khi cai.
pause
goto :eof

:pipfail
echo Cai thu vien that bai. Kiem tra ket noi mang roi chay lai file nay.
pause
