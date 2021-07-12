# Import libraries
import os
import json
import subprocess 

from bit import *
from web3 import Web3
from constants import *
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
from eth_account import Account 
from bit.network import NetworkAPI
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from bit import Key, PrivateKey, PrivateKeyTestnet

load_dotenv

# Web3 connection and 
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


# Load mnemonic and private key
mnemonic = os.getenv('MNEMONIC')
eth_pk= os.getenv("PRIVATE_KEY")


# Create function to call the php file
def derive_wallets(mnemonic, coin, numderive):
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json' 
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    keys = json.loads(output)
    return  keys
 

# Create a coin object to hold child wallets
coins = {"eth", "btc-test", "btc"}
numderive = 3

# Setting the dictionarry
keys = {}
for coin in coins:
    keys[coin]= derive_wallets(os.getenv('mnemonic'), coin, numderive=3)

# Creating a private keys object
eth_PrivateKey = keys["eth"][0]['privkey']
btc_PrivateKey = keys['btc-test'][0]['privkey']
print(json.dumps(eth_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(btc_PrivateKey, indent=4, sort_keys=True))
print(json.dumps(keys, indent=4, sort_keys=True))


# Convert private key string 
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    
eth_acc = priv_key_to_account(ETH,eth_PrivateKey)
btc_acc = priv_key_to_account(BTCTEST,btc_PrivateKey)
print(eth_acc)
print(btc_acc)


# Create transaction with necesseary metadata
def create_tx(coin, account, recipient, amount):
    global tx_data
    if coin ==ETH:
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": recipient, "value": amount}
        )
        tx_data = {
            "to": recipient,
            "from": account.address,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address)
        }
        return tx_data

    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)]) 

# Create, sign, send the transaction 
def send_tx(coin, account, recipient, amount):
    if coin == "eth": 
        trx_eth = create_tx(coin,account, recipient, amount)
        sign = account.signTransaction(trx_eth)
        result = w3.eth.sendRawTransaction(sign.rawTransaction)
        print(result.hex())
        return result.hex()
    else:
        trx_btctest= create_tx(coin,account,recipient,amount)
        sign_trx_btctest = account.sign_transaction(trx_btctest)
        from bit.network import NetworkAPI
        NetworkAPI.broadcast_tx_testnet(sign_trx_btctest)       
        return sign_trx_btctest

# BTC test transactions¶
# create BTC transaction
print(create_tx(BTCTEST,btc_acc,"mkwqRYLAfeoMJnnb5A9WegujdggyBeEPGD", 0.001))
# send BTC transaction
print(send_tx(BTCTEST,btc_acc,'mkwqRYLAfeoMJnnb5A9WegujdggyBeEPGD',0.001))



# ETH transactions
#check  balance of the account
w3.eth.getBalance("0xdEf1cD01019548e6dd77258A515d56bD73745F92")
# create eth transaction
create_tx(ETH,eth_acc,"0x6Fc773e5ba55c2c3A5d055377E54d4141E34c267", 10.000000003333333333)
# send eth transaction
send_tx(ETH, eth_acc,"0x6Fc773e5ba55c2c3A5d055377E54d4141E34c267", 0.000000003333333333)















