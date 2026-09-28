#!/usr/bin/env bash
# ==============================================================================
# PocketSmart AI: Startup & Launcher Script
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT="${1:-8080}"

echo "=========================================================="
echo "   🤖 POCKETSMART AI: Smart Budget & Recommendation Assistant"
echo "=========================================================="
echo "📍 Project Directory: $DIR"
echo "🌐 Starting server on port $PORT..."
echo ""

# Ensure database is initialized & seeded
python3 backend/database.py
python3 backend/seed_data.py

echo ""
echo "✨ PocketSmart AI is ready!"
echo "👉 Open your browser at: http://localhost:$PORT/"
echo ""
echo "Press Ctrl+C to stop the server."
echo "=========================================================="

python3 backend/server.py "$PORT"
