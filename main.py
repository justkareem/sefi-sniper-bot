import asyncio
import base64
import websockets
import json
import requests
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig

WALLET_PUBLIC_KEY = "xxx"
WALLET_PRIVATE_KEY = "xxx"
url = base64.b64decode("aHR0cHM6Ly9wdW1wcG9ydGFsLmZ1bi9hcGkvdHJhZGUtbG9jYWw=").decode("utf-8")
uri = base64.b64decode("d3NzOi8vcHVtcHBvcnRhbC5mdW4vYXBpL2RhdGE=").decode("utf-8")


def execute_trade(data, amount, use_sol):
    print("Starting trade execution...")
    print(f"Input data: {data}")
    print(f"Trade amount: {amount}")
    print(f"Denominated in SOL: {'true' if use_sol else 'false'}")

    payload = {
        "publicKey": WALLET_PUBLIC_KEY,
        "action": "buy",  # "buy" or "sell"
        "mint": data["mint"],  # contract address of the token you want to trade
        "amount": amount,  # amount of SOL or tokens to trade
        "denominatedInSol": "true" if use_sol else "false",  # "true" if amount is SOL, "false" if tokens
        "slippage": 10,  # percent slippage allowed
        "priorityFee": 0.005,  # amount used to enhance transaction speed
        "pool": "pump"  # exchange to trade on. "pump" or "raydium"
    }
    print(f"Payload for initial request: {payload}")

    response = requests.post(url, data=payload)
    print(f"Response from initial request: {response.status_code} - {response.text}")

    try:
        keypair = Keypair.from_base58_string(WALLET_PRIVATE_KEY)
        print("Keypair successfully created.")

        tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [keypair])
        print("Transaction object created.")

        commitment = CommitmentLevel.Confirmed
        config = RpcSendTransactionConfig(skip_preflight=True)
        txPayload = SendVersionedTransaction(tx, config).to_json()
        print(f"Transaction payload: {txPayload}")

        response = requests.post(
            url="xxx",
            headers={"Content-Type": "application/json"},
            data=txPayload
        )
        print(f"Response from RPC endpoint: {response.status_code} - {response.text}")

        response_data = response.json()
        print(f"Response JSON: {response_data}")

        txSignature = response_data.get("result")
        if txSignature is not None:
            print(f'Transaction successful: https://solscan.io/tx/{txSignature}')
        else:
            print("Transaction failed or incomplete.")
            print(response_data)
    except Exception as e:
        print("An error occurred during trade execution:")
        print(str(e))


async def subscribe_and_listen():
    # Prompt the user for input
    print("Select a mode:")
    print("1: Buy token based on coin name")
    print("2: Buy token based on creator")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice not in ["1", "2"]:
        print("Invalid choice. Please restart the program and select 1 or 2.")
        return
    if choice == "1":
        token_name = input("Enter the token name to watch for: ").strip()
    elif choice == "2":
        wallet = input("Enter wallet you wanna track").strip()
    amount = float(input("Enter the amount of SOL or tokens to use for the trade: ").strip())
    use_sol = input("Is the amount entered in SOL? (y/n): ").strip().lower() == "y"

    async with websockets.connect(uri) as websocket:

        # Subscribe based on user choice
        if choice == "1":
            print("Subscribing to token creation events based on coin name...")
            payload = {
                "method": "subscribeNewToken",
            }
            await websocket.send(json.dumps(payload))
        elif choice == "2":
            print("Subscribing to trades made by specific creators...")
            payload = {
                "method": "subscribeAccountTrade",
                "keys": [wallet]  # Replace with desired account keys
            }
            await websocket.send(json.dumps(payload))

        async for message in websocket:
            try:
                data = json.loads(message)

                if choice == "1":
                    # Process token creation events
                    if data.get("name") == token_name:
                        print(f"Token {token_name} created! Proceeding to buy...")
                        execute_trade(data, amount, use_sol)

                elif choice == "2":
                    # Process creator trade events
                    if data.get("txType") == "create" and data.get("pool") == "pump":
                        print("Trade data from creator detected:", data)
                        execute_trade(data, amount, use_sol)

            except json.JSONDecodeError:
                print("Failed to decode message:", message)


# Run the subscription listener
asyncio.run(subscribe_and_listen())
