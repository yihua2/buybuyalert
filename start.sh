#!/bin/bash
# Start BuyBuyAlert app (backend + frontend)

DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate conda
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate paper_trading

echo "Starting backend..."
cd "$DIR/backend"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting frontend..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "BuyBuyAlert is running!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
