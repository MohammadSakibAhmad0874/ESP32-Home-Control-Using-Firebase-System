@echo off
title Stop HomeControl Server
echo  Stopping HomeControl server...
docker compose down
echo  ✅ Server stopped.
pause
