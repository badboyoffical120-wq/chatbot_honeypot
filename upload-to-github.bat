@echo off
REM Automated GitHub Upload Script
REM This script will attempt to install Git and upload your files

echo.
echo ===== GitHub Upload Script =====
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Installing Git...
    echo.
    
    REM Download Git installer
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe', '%TEMP%\GitInstaller.exe')"
    
    if exist "%TEMP%\GitInstaller.exe" (
        echo Running Git installer...
        "%TEMP%\GitInstaller.exe" /QUIET /NORESTART
        timeout /t 10
    ) else (
        echo Failed to download Git installer.
        echo Please download Git manually from: https://git-scm.com/download/win
        pause
        exit /b 1
    )
) else (
    echo Git is already installed.
)

echo.
echo Initializing repository...
git init

echo Adding GitHub user config...
git config user.email "badboyofficial@github.com"
git config user.name "Rahul"

echo.
echo Adding all files...
git add .

echo Committing changes...
git commit -m "Initial commit - Scam detector chatbot with API management"

echo.
echo Checking for remote origin...
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Adding GitHub remote...
    git remote add origin https://github.com/badboyoffical120-wq/chatbot_honeypot.git
)

echo.
echo Setting branch to main...
git branch -M main

echo.
echo Pushing to GitHub (you may be asked to authenticate)...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===== SUCCESS! =====
    echo Your code has been uploaded to GitHub!
    echo Repository: https://github.com/badboyoffical120-wq/chatbot_honeypot
    echo.
    echo Next step: Set up Render deployment at https://render.com
) else (
    echo.
    echo Upload failed. Please check your GitHub credentials.
)

pause
