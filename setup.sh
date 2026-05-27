#!/bin/bash

# JS Recon — setup script
# Installs Python deps into a venv and all optional tools into tools/

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[-]${NC} $1"; }

echo ""
echo "================================================"
echo "  JS Recon — setup"
echo "================================================"
echo ""

# ── Virtual environment ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    ok "Virtual environment created"
else
    warn "Virtual environment already exists, skipping creation"
fi

# Use the venv pip and python for everything from here on
PIP="$VENV_DIR/bin/pip"
PYTHON="$VENV_DIR/bin/python"

# Python requirements
echo ""
echo "[*] Installing Python requirements into venv..."
if "$PIP" install -r requirements.txt -q; then
    ok "jsbeautifier and pytest installed"
else
    err "pip install failed inside venv"
    exit 1
fi

# ── External tools ───────────────────────────────────────────────────────────
mkdir -p tools
cd tools

# LinkFinder
echo ""
echo "[*] Installing LinkFinder..."
if [ -d "LinkFinder" ]; then
    warn "LinkFinder already exists, skipping"
else
    if git clone https://github.com/GerbenJavado/LinkFinder.git -q; then
        "$PIP" install -r LinkFinder/requirements.txt -q
        ok "LinkFinder installed at tools/LinkFinder"
    else
        err "Failed to clone LinkFinder"
    fi
fi

# SecretFinder
echo ""
echo "[*] Installing SecretFinder..."
if [ -d "SecretFinder" ]; then
    warn "SecretFinder already exists, skipping"
else
    if git clone https://github.com/m4ll0k/SecretFinder.git -q; then
        "$PIP" install -r SecretFinder/requirements.txt -q 2>/dev/null || true
        ok "SecretFinder installed at tools/SecretFinder"
    else
        err "Failed to clone SecretFinder"
    fi
fi

cd ..

# trufflehog
echo ""
echo "[*] Installing trufflehog..."
if "$VENV_DIR/bin/trufflehog" --version &>/dev/null 2>&1; then
    warn "trufflehog already installed in venv, skipping"
else
    if "$PIP" install trufflehog -q; then
        ok "trufflehog installed"
    else
        warn "trufflehog install failed (optional, skipping)"
    fi
fi

# prettier
echo ""
echo "[*] Installing prettier..."
if command -v prettier &>/dev/null; then
    warn "prettier already installed, skipping"
else
    if command -v npm &>/dev/null; then
        if npm install -g prettier -q 2>/dev/null; then
            ok "prettier installed"
        else
            warn "prettier install failed — run: sudo npm install -g prettier"
        fi
    else
        warn "npm not found, skipping prettier (optional)"
    fi
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "================================================"
echo -e "  ${GREEN}Setup complete${NC}"
echo "================================================"
echo ""
echo "Activate the venv first, then run:"
echo ""
echo "  source .venv/bin/activate"
echo ""
echo "  python js_recon.py target.har \\"
echo "    --linkfinder tools/LinkFinder/linkfinder.py \\"
echo "    --secretfinder tools/SecretFinder/SecretFinder.py"
echo ""
echo "Or run without activating:"
echo ""
echo "  .venv/bin/python js_recon.py target.har \\"
echo "    --linkfinder tools/LinkFinder/linkfinder.py \\"
echo "    --secretfinder tools/SecretFinder/SecretFinder.py"
echo ""
