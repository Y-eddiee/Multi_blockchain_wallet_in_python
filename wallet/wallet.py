# import libraries
import subprocess
import json
import os

from constants import *
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

load_dotenv()

# Load and set environment variables
load_dotenv()
mnemonic = os.getenv('MNEMONIC')


# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)
    
    
# Create a dictionary object called coins to store the output from `derive_wallets`.
keys = {"btc", "btc-test", "eth"}
numderive = 3

coins = {}
for coin in keys:
    coins[coin]= derive_wallets(mnemonic, coin, numderive=3)

print(json.dumps(coins, indent=2, sort_keys=True))


# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH: 
        gasEstimate = w3.eth.estimateGas(
            {"from":account.address, "to":to, "value": amount}
        )
        return { 
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            #"chain_ID": w3.eth.chain_id
        }
    
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.signTransaction(raw_tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return result.hex()

    elif coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)  

# Send BTCTEST transaction using below code
btc_key = coins[BTCTEST][0]['privkey']
btc_address = coins[BTCTEST][1]['address']
send_tx(BTCTEST, priv_key_to_account(BTCTEST, btc_key),btc_address, 0.0000001)


# Send ETH transaction usinb below code
eth_key = coins[ETH][0]['privkey']
eth_address = coins[ETH][1]['address']
send_tx(ETH, priv_key_to_account(ETH, eth_key),eth_address, 1)