# SEFI Sniper Bot

## 📜 Project Overview
The **SEFI Sniper Bot** is an automated trading bot designed to interact with the Solana blockchain for sniping newly created tokens or trades based on specific wallet activities. The bot uses WebSocket connections for real-time data streaming and automates the buy and sell process with custom block tracking.

## 🚀 Features
- Real-time monitoring of Solana blockchain events.
- Automated wallet generation with private and public keys.
- Automated buy and sell actions based on:
  - Token creation by coin name.
  - Trades initiated by a specific wallet address.
- Block-based sell triggers.
- Secure handling of API keys and private keys.

---

## 🗃️ Project Structure

```
sefi-sniper-bot/
│
├── main.py                # Core bot logic: Handles trading and WebSocket connections.
├── generate_wallet.py     # Generates wallet credentials (API key, public key, private key).
└── README.md              # Project documentation.
```

---

## 🛠️ Installation & Setup

### ✅ Prerequisites
- Python 3.8+
- pip (Python package manager)

### 📦 Install Dependencies
```bash
pip install aiohttp websockets solders solana asyncstdlib requests
```

### 📝 Environment Variables
Create a `.env` file or export these variables:
```bash
export API_KEY=your_generated_api_key
export WALLET_PRIVATE_KEY=your_base58_private_key
export WALLET_PUBLIC_KEY=your_public_key
```

---

## 💡 Usage

### 1️⃣ **Generate a Wallet**
Before running the bot, generate your wallet:
```bash
python generate_wallet.py
```
⚠️ **Important:**
- **Save your `API Key` and `Private Key` securely.**
- **Keys will not be recoverable if lost.**

### 2️⃣ **Run the Sniper Bot**
```bash
python main.py
```
Follow the on-screen prompts:
- Select mode (based on token name or creator wallet).
- Input token name or creator wallet.
- Enter the amount and specify if it’s in SOL.
- Enter the number of blocks after which the bot should sell.

---

## ⚡ File Descriptions

### `main.py`
- Handles:
  - WebSocket subscriptions.
  - Real-time event listening.
  - Buy and sell logic with transaction confirmation.
- Supports error handling and retry mechanisms.

### `generate_wallet.py`
- Generates a wallet via an external API.
- Outputs `API Key`, `Public Wallet Address`, and `Private Key`.
- **Note:** Private and API keys must be stored securely by the user.

---

## ⚡ Security Notice
- **PRIVATE KEY:** Anyone with access can control the wallet. Keep it secure!
- **API KEY:** Essential for bot trading actions. Store it safely.
- Keys are **not recoverable** if lost.

---

## 📜 Contributing
Contributions are welcome! Follow these steps:

1. Fork the repo.
2. Create a new branch: `git checkout -b feature-branch`.
3. Commit your changes: `git commit -m "Add some feature"`.
4. Push to the branch: `git push origin feature-branch`.
5. Open a pull request.

---

## ⚖️ License
This project is licensed under the **MIT License**.

---

## 👨‍💻 Author
**Elelu Abdulkareem Ayomikun**  
[GitHub](https://github.com/justkareem) | [LinkedIn](https://www.linkedin.com/in/elelu-kareem/)

---

## ⚡ Disclaimer
This bot interacts with decentralized blockchain platforms. Use at your own risk. The author holds no responsibility for any losses incurred due to improper use.

