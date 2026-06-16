@echo off
cd /d "C:\Users\19035\Documents\local_agent"
call venv\Scripts\activate
python executive_briefing.py > morning_report.txt
