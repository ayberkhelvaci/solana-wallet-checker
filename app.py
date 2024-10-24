import base58
import pandas as pd
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from flask import Flask, render_template

app = Flask(__name__)

# Function to fetch balance for a Solana address
async def fetch_balance(client, address):
    try:
        pubkey = PublicKey(address)
        balance_data = await client.get_balance(pubkey)
        balance = balance_data['result']['value'] / 1_000_000_000  # Convert lamports to SOL
        return balance
    except Exception as e:
        return 0

# Function to check wallet balances and return addresses over threshold
async def monitor_wallets(threshold=0.01):
    addresses = pd.read_csv("addresses.csv")['Address'].tolist()
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    passed_wallets = []

    for address in addresses:
        balance = await fetch_balance(client, address)
        if balance > threshold:
            passed_wallets.append((address, f"{balance:.4f} SOL"))

    await client.close()
    return passed_wallets

@app.route('/')
async def home():
    wallets_above_threshold = await monitor_wallets()
    return render_template('index.html', wallets=wallets_above_threshold)

if __name__ == '__main__':
    app.run(debug=True)