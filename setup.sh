#!/bin/bash

echo "🚀 EcoTravel Profesyonel Setup"
echo "================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created. Please edit it with your settings.${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create logs directory
echo -e "${YELLOW}Creating logs directory...${NC}"
mkdir -p logs

# Run code formatters
echo -e "${YELLOW}Formatting code...${NC}"
black .
isort .

# Run linters
echo -e "${YELLOW}Running linters...${NC}"
flake8 . || true
pylint **/*.py --exit-zero || true

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
pytest -v || true

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run the application:"
echo "   python app_new.py"
echo ""
echo "Or use Docker:"
echo "   docker-compose up"
echo ""
echo "API Documentation: http://localhost:5000/api/docs"
echo ""
