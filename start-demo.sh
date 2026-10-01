#!/bin/bash
# 一键启动 meal-planner demo

export OPENAI_API_KEY="sk-api-_NRLWqdyOCxGBEdlOvWfK3eoUk1MMDcp73gJC-e9jVnyLG4fmy-nIG1vvb5V7Ia3BO0OdGZDSguAjmnQLbonfYy2k6PcU3gtNr2g4ydIZcxhkLBEnAvDOdw"
export RINX_OCTOS_BIN="/home/windy/Project/octosense-ws/Rinx/target/debug/octos"

# 杀掉旧进程
pkill -f "target/debug/rinx" 2>/dev/null
pkill -f "octos gateway" 2>/dev/null
pkill -f "card-host" 2>/dev/null
sleep 2

echo "=== 启动 Rinx ==="
cd /home/windy/Project/octosense-ws/Rinx
nohup env OPENAI_API_KEY="$OPENAI_API_KEY" RINX_OCTOS_BIN="$RINX_OCTOS_BIN" ./target/debug/rinx > /tmp/rinx-demo.log 2>&1 &
RINX_PID=$!
echo "Rinx PID: $RINX_PID"

sleep 8

echo ""
echo "=== 状态检查 ==="
ps aux | grep -E "rinx|octos" | grep -v grep | head -5
echo ""
echo "=== Rinx 日志（最近）==="
tail -10 /tmp/rinx-demo.log | grep -v "ui_hang\|font\|widget\|thread.rs\|update_state\|send" | head -10
