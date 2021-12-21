import requests
import json
import time
import argparse
import os


def parseArgs():
    arg_parser = argparse.ArgumentParser(
        description='FTM Scan to usable CSV parser', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('--ftmscan-api-key', '-k',
                            default='', help='API key from ftmscan.com')
    arg_parser.add_argument('--wallet-address', '-a', default='',
                            help='Address of wallet for which to retrieve transactions')
    known_args, _unknown_args = arg_parser.parse_known_args()

    return known_args


def fetchContractFiles(contractDir='ftmContracts'):
    curDir = os.getcwd()
    if os.path.exists(contractDir):
        os.system('rm -rf {} > /dev/null 2>&1'.format(contractDir))
    os.system('mkdir -p {} > /dev/null 2>&1'.format(contractDir))
    os.chdir(contractDir)
    os.system('git init > /dev/null 2>&1')
    os.system(
        'git remote add -f origin https://github.com/Fantom-foundation/fantom-api-graphql > /dev/null 2>&1')
    os.system('git config core.sparseCheckout true > /dev/null 2>&1')
    os.system(
        'echo "internal/repository/rpc/contracts/" >> .git/info/sparse-checkout')
    os.system('git pull origin master > /dev/null 2>&1')
    os.chdir(curDir)
    contractContents = []
    fullpath = os.path.join(contractDir, 'internal/repository/rpc/contracts/')
    for filename in os.listdir(fullpath):
        if filename.endswith('.go'):
            with open(os.path.join(fullpath, filename)) as fp:
                contractContents.extend(fp.readlines())
    if os.path.exists(contractDir):
        os.system('rm -rf {} > /dev/null 2>&1'.format(contractDir))
    return contractContents


def getPrepareToWithdrawDelegation(hash):
    r = requests.get('https://ftmscan.com/tx/{}#eventlog'.format(hash))
    lines = r.content.decode('ascii', 'ignore').split('\n')
    for line in lines:
        if 'chunk_ori_2_1' in line:
            return float(int(line.split("chunk_ori_2_1'>")[1].split('</span>')[0], 16))/1000000000000000000


def getClaimDelegationRewards(hash):
    r = requests.get('https://ftmscan.com/tx/{}#eventlog'.format(hash))
    lines = r.content.decode('ascii', 'ignore').split('\n')
    for line in lines:
        if 'chunk_ori_1_1' in line:
            return float(int(line.split("chunk_ori_1_1'>")[1].split('</span>')[0], 16))/1000000000000000000


def decodeTransaction(hash, pwaWallet, methodID, timestamp, fee):
    walletString = "My PWA Wallet"
    r = requests.get('https://ftmscan.com/tx/{}'.format(hash))
    lines = r.content.decode('ascii', 'ignore').split('\n')
    price = ''
    status = 'Success'
    transactionstoPrint = []
    for line in lines:
        if 'ContentPlaceHolder1_spanClosingPrice' in line:
            price = line.replace(
                ' / FTM</span>', '').replace('<span id="ContentPlaceHolder1_spanClosingPrice">', '')
        if 'Status:' in line:
            if '</i>Fail</span>' in line:
                status = 'Fail'
    for line in lines:
        if 'View Contract Internal Transactions' in line:
            transfers = line.split('TRANSFER')
            for transfer in transfers:
              if '</span> &nbsp;' in transfer:
                sentLine = transfer.split('</span> &nbsp;')[1].replace(
                    "<b>.</b>", '.').split("<span class='text-secondary'>")

                value = sentLine[0].replace(',', '').replace(
                    '(', '').replace(')', '')
                fromAddress = sentLine[1].split(
                    "' class='hash-tag text-truncate'")[0].split("From</span> <a href='/address/")[1]
                toAddress = sentLine[2].split(
                    "<a href='/address/")[1].split("' ")[0]
                token = value.split(' ')[1]
                value = value.split(' ')[0]
                transactionstoPrint.append("{},{},{},{},{},{},{},{},{},{}".format(
                    value, token, fromAddress, toAddress, hash, methodID, timestamp, fee, price, status))
        if 'Tokens Transferred:' in line:
            toAddress = ''
            fromAddress = ''
            transfers = line.replace("</b> </span><span class='hash-tag text-truncate  mr-1'><a href='/token/", ' ')\
                .replace("'><span class='hash-tag text-truncate hash-tag-custom-from tooltip-address' data-toggle='tooltip' title='", " ")\
                .replace("</span></a></span><span class='mr-1'>", "")\
                .replace("<span class='hash-tag text-truncate hash-tag-custom-to tooltip-address' data-toggle='tooltip' title='", " ")\
                .replace("</a></div></li></ul></div></div>", "").split("<b>")
            for x in transfers:
                if not 'Tokens Transferred: ' in x:
                    if x.startswith('From'):
                        fromAddress = x.split("'>")[1]
                    elif x.startswith('To'):
                        toAddress = x.split("'>")[-1]
                    elif x.startswith('For'):
                        x = x.replace("</a></div></li><li class='media align-items-baseline mb-2'><span class='row-count text-secondary small mr-1'><i class='fa fa-caret-right'></i></span><div class='media-body'><span class=''>", "")\
                            .replace(" </a></div></li></ul></div></div>", "")\
                            .replace("For</b> </span><span class='mr-1'>", "")
                        if 'WFTM' in x:
                            value = x.split('WFTM">')[1].split(' ')[0]
                            token = x.split('WFTM">')[1].split(
                                ' ')[-1].replace('(', '').replace(')', '')
                        else:
                            value = x.split(" ")[0]
                            if "<span" in value:
                                value = x.split('">')[1].split(" ")[0]
                            token = x.strip().split(
                                " ")[-1].replace('(', '').replace(')', '')
                            if "color=''>" in x:
                                token = x.split("title='")[-1].split("'><")[0]
                        transactionstoPrint.append("{},{},{},{},{},{},{},{},{},{}".format(value.replace(
                            ',', ''), token, fromAddress, toAddress, hash, methodID, timestamp, fee, price, status))

    if len(transactionstoPrint) == 0:
        value = ''
        token = ''
        toAddress = ''
        fromAddress = ''
        if methodID == 'CreateDelegation':
            token = 'FTM'
            value = getClaimDelegationRewards(hash)
            toAddress = '0xfc00face00000000000000000000000000000000'
            fromAddress = pwaWallet
        if methodID == 'PrepareToWithdrawDelegation':
            token = 'FTM'
            value = getPrepareToWithdrawDelegation(hash)
            toAddress = pwaWallet
            fromAddress = '0xfc00face00000000000000000000000000000000'
        if methodID == 'ClaimDelegationRewards':
            token = 'FTM'
            value = getClaimDelegationRewards(hash)
            toAddress = pwaWallet
            fromAddress = '0xfc00face00000000000000000000000000000000'
        transactionstoPrint.append("{},{},{},{},{},{},{},{},{},{}".format(
            value, token, fromAddress, toAddress, hash, methodID, timestamp, fee, price, status))

    with open('transactions.csv', 'a') as f:
        for tx in transactionstoPrint:
          line = tx.replace(pwaWallet, walletString)
          if walletString in line or ",,," in line:
            f.write('{}\n'.format(line))


if __name__ == '__main__':
    args = parseArgs()
    PWA_address = args.wallet_address
    APIKEY = args.ftmscan_api_key

    transactions = 'https://api.ftmscan.com/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&sort=asc&apikey={}'.format(
        PWA_address, APIKEY)
    tokenTransactions = 'https://api.ftmscan.com/api?module=account&action=tokentx&address={}&startblock=0&endblock=99999999&sort=asc&apikey={}'.format(
        PWA_address, APIKEY)
    transactionsR = requests.get(transactions)
    transactionsResult = json.loads(transactionsR.content)['result']
    tokenTransactionsR = requests.get(tokenTransactions)
    tokenTransactionsResult = json.loads(tokenTransactionsR.content)['result']

    with open('transactions.csv', 'w') as f:
        f.write(
            "Value,Token,From,To,Hash,Method,Timestamp,Fee,HistoricalPrice,Status\n")

    contractContents = fetchContractFiles()

    transactionHashes = {}

    for transaction in tokenTransactionsResult:
      transactionHashes[transaction['hash']] = {}
      transactionHashes[transaction['hash']]['timeStamp'] = transaction['timeStamp']
      gasUsed = int(transaction['gasUsed']) * int(transaction['gasPrice'])
      gasUsed = float(gasUsed)/1000000000000000000
      transactionHashes[transaction['hash']]['gasUsed'] = gasUsed
      input = transaction['input'][0:10]
      for line in contractContents:
        if "{}.".format(input) in line:
          input = line.split(' ')[1]
          break
      transactionHashes[transaction['hash']]['input'] = input

    for transaction in transactionsResult:
      transactionHashes[transaction['hash']] = {}
      transactionHashes[transaction['hash']]['timeStamp'] = transaction['timeStamp']
      gasUsed = int(transaction['gasUsed']) * int(transaction['gasPrice'])
      gasUsed = float(gasUsed)/1000000000000000000
      transactionHashes[transaction['hash']]['gasUsed'] = gasUsed
      input = transaction['input'][0:10]
      for line in contractContents:
        if "{}.".format(input) in line:
          input = line.split(' ')[1]
          break
      transactionHashes[transaction['hash']]['input'] = input

    for hash in transactionHashes:
      decodeTransaction(hash, PWA_address, transactionHashes[hash]['input'], transactionHashes[hash]['timeStamp'], transactionHashes[hash]['gasUsed'])
      time.sleep(3)
