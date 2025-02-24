import asyncio
import base64
import json
import os
import aiohttp
import websockets
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from solana.rpc.websocket_api import connect
from asyncstdlib import enumerate

API_KEY = os.environ.get("API_KEY", "your_default_api_key")
WALLET_PRIVATE_KEY = os.environ.get("WALLET_PRIVATE_KEY", "your_base58_private_key")
WALLET_PUBLIC_KEY = os.environ.get("WALLET_PUBLIC_KEY", "your_public_key")

TRADE_URL = base64.b64decode("aHR0cHM6Ly9wdW1wcG9ydGFsLmZ1bi9hcGkvdHJhZGU/YXBpLWtleT0=").decode("utf-8") + API_KEY
DATA_URI = base64.b64decode("d3NzOi8vcHVtcHBvcnRhbC5mdW4vYXBpL2RhdGE=").decode("utf-8")
QUICKNODE_URL = "wss://wild-compatible-tree.solana-mainnet.quiknode.pro/9f0d6a1e292c4ee177bd2a6270446999e6d5d092/"


async def async_post(session, url, data, headers=None, return_bytes=False):
    async with session.post(url, data=data, headers=headers) as response:
        if return_bytes:
            return await response.read()
        return await response.text()


async def async_get(session, url, headers=None):
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def keepalive(ws, interval=10):
    while True:
        try:
            await asyncio.sleep(interval)
            pong_waiter = await ws.ping()
            await asyncio.wait_for(pong_waiter, timeout=interval)
        except Exception as e:
            print(f"Ping error: {e}")
            break


async def sell_option(num_of_blocks, buy_block, mint, session):
    while True:
        try:
            async with connect(QUICKNODE_URL, ping_interval=None) as ws:
                # Start keepalive ping task.
                ping_task = asyncio.create_task(keepalive(ws))
                await ws.slot_subscribe()
                first_resp = await ws.recv()  # Initial subscription response
                async for idx, msg in enumerate(ws):
                    slot = msg[0].result.slot
                    if (slot - buy_block) == num_of_blocks:
                        print("Block threshold reached. Initiating sell order...")
                        sell_payload = {
                            "publicKey": WALLET_PUBLIC_KEY,
                            "action": "sell",
                            "mint": mint,
                            "amount": "100%",
                            "denominatedInSol": "false",
                            "slippage": 10,
                            "priorityFee": 0.005,
                            "pool": "auto"
                        }
                        sell_response = await async_post(session, "https://pumpportal.fun/api/trade-local",
                                                         data=sell_payload, return_bytes=True)
                        try:
                            keypair = Keypair.from_base58_string(WALLET_PRIVATE_KEY)
                        except Exception as e:
                            print(f"Error creating keypair: {e}")
                            return

                        try:
                            vt = VersionedTransaction.from_bytes(sell_response)
                        except Exception as e:
                            print(f"Error decoding transaction bytes: {e}")
                            return

                        tx = VersionedTransaction(vt.message, [keypair])
                        config = RpcSendTransactionConfig(skip_preflight=True)
                        txPayload = SendVersionedTransaction(tx, config).to_json()
                        headers = {"Content-Type": "application/json"}
                        solana_response_text = await async_post(session, "https://api.mainnet-beta.solana.com/",
                                                                data=txPayload, headers=headers)
                        try:
                            solana_response = json.loads(solana_response_text)
                            txSignature = solana_response.get('result')
                            print(f'Transaction sent: https://solscan.io/tx/{txSignature}')
                        except Exception as e:
                            print(f"Error parsing Solana response: {e}")
                        ping_task.cancel()
                        return
        except Exception as e:
            print(f"Error in sell_option connection: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


# --------------------------------------------------
# Execute Trade: Initiates a buy order then monitors the trade status.
# --------------------------------------------------
async def execute_trade(data, amount, use_sol, num_of_blocks, session):
    print("Starting trade execution...")
    print(f"Input data: {data}")
    print(f"Trade amount: {amount}")
    print(f"Denominated in SOL: {'true' if use_sol else 'false'}")

    payload = {
        "action": "buy",
        "mint": data["mint"],
        "amount": amount,
        "denominatedInSol": "true" if use_sol else "false",
        "slippage": 10,
        "priorityFee": 0.005,
        "pool": "pump",
    }
    print(f"Payload for buy order: {payload}")

    trade_response_text = await async_post(session, TRADE_URL, data=payload)
    try:
        response_data = json.loads(trade_response_text)
    except Exception as e:
        print(f"Error decoding trade response: {e}")
        return

    signature = response_data.get("signature")
    if signature is None:
        print(f"Buy transaction not successful: {response_data}")
        return

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,ro;q=0.8",
        "origin": "https://solscan.io",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sol-aut": "KOsxksAFeRJFrTrBB9dls0fKJirhtYj7o=ptJR-4",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }

    tx_detail_url = f"https://api-v2.solscan.io/v2/transaction/detail?tx={signature}"
    solscan_response_text = await async_get(session, tx_detail_url, headers=headers)
    try:
        solscan_response = json.loads(solscan_response_text)
    except Exception as e:
        print(f"Error parsing Solscan response: {e}")
        return

    tx_status = solscan_response.get("success")
    if not tx_status:
        print("Buy transaction did not land")
        return

    tx_block = solscan_response.get("data", {}).get("block_id")
    print("Buy transaction confirmed. Monitoring blocks for sell trigger...")
    await sell_option(num_of_blocks, tx_block, data["mint"], session)


# --------------------------------------------------
# Subscribe and Listen: Handles user input and event subscriptions via WebSocket.
# Implements a retry mechanism in case the WebSocket disconnects.
# --------------------------------------------------
async def subscribe_and_listen():
    print("Select a mode:")
    print("1: Buy token based on coin name")
    print("2: Buy token based on creator")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice not in ["1", "2"]:
        print("Invalid choice. Please restart the program and select 1 or 2.")
        return

    token_name = None
    wallet = None
    if choice == "1":
        token_name = input("Enter the token name to watch for: ").strip()
    elif choice == "2":
        wallet = input("Enter the wallet to track: ").strip()

    amount = float(input("Enter the amount of SOL or tokens to use for the trade: ").strip())
    use_sol = input("Is the amount entered in SOL? (y/n): ").strip().lower() == "y"
    num_of_blocks = int(input("Enter number of blocks to activate sell: "))

    async with aiohttp.ClientSession() as session:
        # Wrap the subscription connection in a retry loop.
        while True:
            try:
                async with websockets.connect(DATA_URI, ping_interval=None) as websocket:
                    # Start the keepalive task.
                    ping_task = asyncio.create_task(keepalive(websocket))
                    if choice == "1":
                        print("Subscribing to token creation events based on coin name...")
                        payload = {"method": "subscribeNewToken"}
                        await websocket.send(json.dumps(payload))
                    elif choice == "2":
                        print("Subscribing to trades made by specific creators...")
                        payload = {
                            "method": "subscribeAccountTrade",
                            "keys": [wallet]
                        }
                        await websocket.send(json.dumps(payload))
                    # Process incoming messages.
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            if choice == "1":
                                # Process token creation events.
                                if data.get("name") == token_name:
                                    print(f"Token {token_name} created! Proceeding to buy...")
                                    await execute_trade(data, amount, use_sol, num_of_blocks, session)
                            elif choice == "2":
                                # Process creator trade events.
                                if data.get("txType") == "create" and data.get("pool") == "pump":
                                    print("Trade data from creator detected:", data)
                                    await execute_trade(data, amount, use_sol, num_of_blocks, session)
                        except json.JSONDecodeError:
                            print("Failed to decode message:", message)
                    ping_task.cancel()
            except Exception as e:
                print(f"WebSocket connection error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)


def main():
    asyncio.run(subscribe_and_listen())


if __name__ == "__main__":
    main()
