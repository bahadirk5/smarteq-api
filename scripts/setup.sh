#!/bin/bash

# Exit on error
set -e

# Variables
PROJECT_NAME="smarteq"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up ${PROJECT_NAME} project...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python could not be found. Please install Python 3.8+ and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install development requirements
echo -e "${BLUE}Installing development requirements...${NC}"
pip install -r requirements/development.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please edit it with your actual credentials!${NC}"
fi

# Run migrations
echo -e "${BLUE}Running migrations...${NC}"
python manage.py migrate

# Create superuser
echo -e "${BLUE}Do you want to create a superuser? (y/n)${NC}"
read create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# Collect static files
echo -e "${BLUE}Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}Setup completed! You can now start the development server with:${NC}"
echo -e "python manage.py runserver"