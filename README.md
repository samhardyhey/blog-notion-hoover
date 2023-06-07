## Blog Notion Hoover
Notebooks and scripts for the:

- Conversion/parsing of nautilus epub issues
- TTS sampling
- Bulk TTS conversion using a Coqui VKTS multi-speaker model (speaker randomly selected)

See the accompanying blog post [here](https://www.samhardyhey.com/behold-the-humble-nautilus).

## Install
- For epub conversion/parsing and TTS, create env via `scripts/create_env.sh`

## Usage
- **Parsing/conversion.** Via `python transform/ebook.py`
- **TTS transforms.** Via `python transform/tts.py`
- **Streaming API.** Via `docker-compose up --build -d`

All code obviously dependant upon Nautilus issues, S3 bucket access, some decent hardware to run the TTS conversions.