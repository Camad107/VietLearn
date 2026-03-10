#!/bin/bash
cd /home/claude-user/vietlearn
exec uvicorn app:app --host 0.0.0.0 --port 8070 --workers 1
