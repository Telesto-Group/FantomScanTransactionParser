# FantomScanTransactionParser
Combines the faulty ftmscan api with the faulty ftmscan web interface for a more correct transaction history.  Takes a wallet address and a ftm scan api key and outputs information to `transactions.csv`


1. install git and python: `apt-get update && apt-get install git python -y`

1. clone this repo: `git clone https://github.com/Telesto-Group/FantomScanTransactionParser`

1. install python dependencies: `pip install -r requirements.txt`

1. obtain an api key from [ftmscan](https://ftmscan.com/)

1. run the python script: `python ftmscan.py -a <wallet address> -k <api key>`
