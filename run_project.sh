#!/bin/bash

# Configuration
VENV_DIR="venv"
PYTHON_CMD="python3"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚗 AutoÉcole Pro - Gestionnaire de lancement${NC}"

# 1. Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    $PYTHON_CMD -m venv $VENV_DIR
fi

# 2. Activate virtual environment
echo -e "${BLUE}🔌 Activation de l'environnement venv...${NC}"
source $VENV_DIR/bin/activate

# 3. Install/Update dependencies
echo -e "${BLUE}📥 Installation des dépendances...${NC}"
pip install -r requirements.txt --quiet

# 4. Prepare database
echo -e "${BLUE}💽 Application des migrations...${NC}"
python manage.py migrate

# 5. Seed data (optional but recommended for first time)
echo -e "${BLUE}🌱 Peuplement de la base de données...${NC}"
python seed_data.py

# 6. Launch server
echo -e "${GREEN}🚀 Lancement du serveur à l'adresse http://127.0.0.1:8000/${NC}"
python manage.py runserver
