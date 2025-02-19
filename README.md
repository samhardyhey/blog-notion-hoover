# Notion Hoover 🧹

Tools for ingesting and classifying bookmarked content from social platforms into Notion. Companion code for ["Notion Hoover"](https://www.samhardyhey.com/notion-hoover).

## Features
- 📥 Social media content ingestion
- 🏷️ Automated content classification
- 📊 Argilla-based evaluation
- 📝 Notion integration

## Platforms
- 🐦 Twitter
- 📱 Reddit
- 💻 GitHub
- 👥 LinkedIn

## Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
# Run content ingestion
python main.py

# Start Argilla evaluation
cd evaluate
docker-compose up -d
python evaluate.py
```

## Structure
- 🔄 `main.py` # Content ingestion
- 📊 `evaluate/` # Classification evaluation
- ⚙️ `requirements.txt` # Dependencies

*Note: Requires platform-specific API credentials.*