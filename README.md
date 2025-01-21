# Pump Portal Trade Bot

This project allows you to monitor and execute trades on specified tokens or creators in real time.

## Features

- Monitor token creation events based on token name.
- Track trades by specific wallet creators.
- Execute trades seamlessly with customizable parameters.

## Prerequisites

Ensure you have the following installed:

- Python 3.8 or higher
- Required Python libraries (see `requirements.txt`)

## Setup

1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your wallet keys in `main.py`:
   ```python
   WALLET_PUBLIC_KEY = "YourPublicKeyHere"
   WALLET_PRIVATE_KEY = "YourPrivateKeyHere"
   ```

## Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. Follow the prompts:
   - Select whether to monitor tokens by name or track a creator's trades.
   - Provide the required details (e.g., token name, creator wallet, amount).
   - Specify whether the amount is in SOL or tokens.

3. The bot will subscribe to the specified events and execute trades automatically when conditions are met.

## Notes

- Ensure you have a valid RPC endpoint for Solana transactions configured in the script.
- Monitor the console for transaction status and trade confirmations.

## Requirements

Refer to `requirements.txt` for all dependencies.

---

Happy Trading!