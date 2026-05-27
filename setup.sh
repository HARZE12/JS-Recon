#!/bin/bash

# JS Recon — setup script
# Installs Python deps and all optional tools into a tools/ directory

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

# Python requirements
echo "[*] Installing Python requirements..."
if pip install -r requirements.txt -q; then
    ok "jsbeautifier and pytest installed"
else
    err "pip install failed — make sure Python 3 and pip are available"
    exit 1
fi

# Create tools directory
mkdir -p tools
cd tools

# LinkFinder
echo ""
echo "[*] Installing LinkFinder..."
if [ -d "LinkFinder" ]; then
    warn "LinkFinder already exists, skipping"
else
    if git clone https://github.com/GerbenJavado/LinkFinder.git -q; then
        pip install -r LinkFinder/requirements.txt -q
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
        pip install -r SecretFinder/requirements.txt -q 2>/dev/null || true
        ok "SecretFinder installed at tools/SecretFinder"
    else
        err "Failed to clone SecretFinder"
    fi
fi

cd ..

# trufflehog
echo ""
echo "[*] Installing trufflehog..."
if command -v trufflehog &>/dev/null; then
    warn "trufflehog already installed, skipping"
else
    if pip install trufflehog -q; then
        ok "trufflehog installed"
    else
        err "Failed to install trufflehog"
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

# Done — print usage with correct paths
echo ""
echo "================================================"
echo -e "  ${GREEN}Setup complete${NC}"
echo "================================================"
echo ""
echo "Run:"
echo ""
echo "  python js_recon.py target.har \\"
echo "    --linkfinder tools/LinkFinder/linkfinder.py \\"
echo "    --secretfinder tools/SecretFinder/SecretFinder.py"
echo ""
echo "Or add these as defaults by editing the argument defaults in js_recon.py"
echo ""
