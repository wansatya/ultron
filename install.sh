#!/bin/bash
# Ultron Installation Script
# Usage: curl -sSL https://raw.githubusercontent.com/wansatya/ultron/main/install.sh | bash

set -e

echo "============================================================"
echo "Ultron Installation Script"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.9 or higher and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}Error: Python 3.9+ required (you have $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Check if git is available
if command -v git &> /dev/null; then
    HAS_GIT=true
else
    HAS_GIT=false
fi

# Installation directory
INSTALL_DIR="${INSTALL_DIR:-$HOME/ultron}"

echo "Installation directory: $INSTALL_DIR"
echo ""

# Clone or download
if [ "$HAS_GIT" = true ]; then
    echo "Cloning Ultron repository..."
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}Warning: Directory already exists. Updating...${NC}"
        cd "$INSTALL_DIR"
        git pull
    else
        git clone https://github.com/wansatya/ultron.git "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
else
    echo "Downloading Ultron..."
    # Fallback: download zip (requires GitHub release)
    TEMP_ZIP="/tmp/ultron.zip"
    curl -sSL https://github.com/wansatya/ultron/archive/main.zip -o "$TEMP_ZIP"
    unzip -q "$TEMP_ZIP" -d /tmp/
    mkdir -p "$INSTALL_DIR"
    cp -r /tmp/ultron-main/* "$INSTALL_DIR/"
    rm -rf /tmp/ultron-main "$TEMP_ZIP"
    cd "$INSTALL_DIR"
fi

echo -e "${GREEN}✓ Ultron downloaded${NC}"
echo ""

# Create virtual environment (optional but recommended)
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "This may take 5-10 minutes on first install (downloading ~1.5GB of ML models)"
echo ""

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create data directories
mkdir -p data/models data/sessions

# Check for bot token
echo "============================================================"
echo "Configuration"
echo "============================================================"
echo ""

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠ TELEGRAM_BOT_TOKEN not set${NC}"
    echo ""
    echo "To complete setup:"
    echo "1. Get a bot token from @BotFather on Telegram"
    echo "2. Set the token:"
    echo "   export TELEGRAM_BOT_TOKEN='your-token-here'"
    echo "3. Add to your shell profile to make permanent:"
    echo "   echo 'export TELEGRAM_BOT_TOKEN=\"your-token\"' >> ~/.bashrc"
    echo ""
else
    echo -e "${GREEN}✓ TELEGRAM_BOT_TOKEN is set${NC}"
    echo ""
fi

# Create convenience script
cat > run_ultron.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python -m ultron.main
EOF

chmod +x run_ultron.sh

echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo -e "${GREEN}✓ Ultron installed successfully${NC}"
echo ""
echo "Location: $INSTALL_DIR"
echo ""
echo "To run Ultron:"
echo "  cd $INSTALL_DIR"
echo "  ./run_ultron.sh"
echo ""
echo "Or:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python -m ultron.main"
echo ""
echo "Documentation:"
echo "  - QUICKSTART.md - Quick start guide"
echo "  - README.md - Full documentation"
echo "  - INSTALL.md - Installation details"
echo ""
echo "Next steps:"
echo "  1. Get a Telegram bot token from @BotFather"
echo "  2. Set TELEGRAM_BOT_TOKEN environment variable"
echo "  3. Run Ultron with ./run_ultron.sh"
echo ""
