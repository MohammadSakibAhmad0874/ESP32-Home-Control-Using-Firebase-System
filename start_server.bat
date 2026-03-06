@echo off
title HomeControl Server

echo.
echo  ============================================
echo   HomeControl - Self-Hosted Server Launcher
echo   Domain: cespitosely-exiguous-homer.ngrok-free.dev
echo  ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Docker Desktop is not running!
    echo  Please start Docker Desktop first, then run this again.
    pause
    exit /b 1
)

echo  [1/3] Starting Docker services (Backend + PostgreSQL + Nginx)...
docker compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Docker failed to start. Check logs with: docker compose logs
    pause
    exit /b 1
)

echo  [2/3] Waiting for server to be ready...
timeout /t 5 /nobreak >nul

echo  [3/3] Starting Ngrok tunnel (permanent URL)...
start "Ngrok Tunnel" cmd /k "ngrok start homecontrol --config ngrok.yml"

echo.
echo  ============================================
echo  ✅ HomeControl is LIVE!
echo.
echo  Local:  http://localhost/
echo  Global: https://cespitosely-exiguous-homer.ngrok-free.dev/
echo  API:    http://localhost/api/docs
echo  ============================================
echo.
pause
