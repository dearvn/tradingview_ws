# Information
This package to fetch data from tradingview websocket
## Installation
```bash

# Create an isolated Python virtual environment
pip3 install virtualenv
virtualenv ./virtualenv --python=$(which python3)

# Activate the virtualenv
# IMPORTANT: it needs to be activated every time before you run
. virtualenv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Install cointrol-*
pip install -e .

# run test
python -m test