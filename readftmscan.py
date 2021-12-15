import requests
import json

walletString = "My PWA Wallet"

transactions = 'https://api.ftmscan.com/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&sort=asc&apikey={}'.format(PWA_address, APIKEY)
transactionsR = requests.get(transactions)
transactionsResult = json.loads(transactionsR.content)['result']

tokenTransfers='https://api.ftmscan.com/api?module=account&action=tokentx&address={}&startblock=0&endblock=999999999&sort=asc&apikey={}'.format(PWA_address, APIKEY)
tokenTransfersR = requests.get(tokenTransfers)
tokenTransferResult = json.loads(tokenTransfersR.content)['result']

print("Value,Token,From,To,Hash")
def decodeTransaction(hash):
  r = requests.get('https://ftmscan.com/tx/{}'.format(hash))
  lines = r.content.decode('ascii', 'ignore').split('\n')
  for line in lines:
    if 'View Contract Internal Transactions' in line:
      sentLine = line.split('TRANSFER</span> &nbsp;')[1].replace("<b>.</b>", '.').split("<span class='text-secondary'>")
      value = sentLine[0].replace(',', '').replace('(', '').replace(')', '')
      fromAddress = sentLine[1].split("' class='hash-tag text-truncate'")[0].split("From</span> <a href='/address/")[1]
      toAddress = sentLine[2].split("<a href='/address/")[1].split("' ")[0]
      token = value.split(' ')[1]
      value = value.split(' ')[0]
      print("{},{},{},{},{}".format(value, token, fromAddress.replace(pwaWallet, walletString), toAddress.replace(pwaWallet, walletString), hash))
    if 'Tokens Transferred:' in line:
      toAddress = ''
      fromAddress = ''
      transfers = line.replace("</b> </span><span class='hash-tag text-truncate  mr-1'><a href='/token/",' ')\
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
              token = x.split('WFTM">')[1].split(' ')[-1].replace('(', '').replace(')', '')
            else:
              value = x.split(" ")[0]
              if "<span" in value:
                value = x.split('">')[1].split(" ")[0]
              token = x.strip().split(" ")[-1].replace('(', '').replace(')', '')
              if "color=''>" in x:
                token = x.split("title='")[-1].split("'><")[0]
            print("{},{},{},{},{}".format(value.replace(',', ''), token, fromAddress.replace(pwaWallet, walletString), toAddress.replace(pwaWallet, walletString), hash))

for transaction in transactionsResult:
  decodeTransaction(transaction['hash'])
