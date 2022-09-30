# FantomScanTransactionParser
Combines the faulty ftmscan api with the faulty ftmscan web interface for a more correct transaction history.  Takes a wallet address and a ftm scan api key and outputs information to `transactions.csv`


1. install git and python: `apt-get update && apt-get install git python -y`

1. clone this repo: `git clone https://github.com/mhetzel/FantomScanTransactionParser`

1. install python dependencies: `pip install -r requirements.txt`

1. obtain an api key from [ftmscan](https://ftmscan.com/)

1. run the python script: `python ftmscan.py -a <wallet address> -k <api key>`

1. additional arguments:
    - --before-timestamp <unix_timestamp>
    - --after-timestamp <unix_timestamp>
    - --hash <transaction_hash>
    - --verbose
    - --ignore-failed
    - --ignore-zero-value


### tip
get unix timestamps from [epochconverter](https://www.epochconverter.com/)

### read all transactions between 1662073776 and 1654008637 ignoring failed and empty transactions
example: python3 readftmscan.py -bt 1662073776 -at 1654008637 -v -a <address> -k <key> -if -izv