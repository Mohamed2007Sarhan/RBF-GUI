# Bitcoin Testnet RBF Transaction Chain Demo

This repository contains Python scripts to demonstrate Replace-By-Fee (RBF) dynamics and mempool ancestry on Bitcoin Testnet.

## Overview

The scripts demonstrate:
1. Creating a parent transaction with minimum fees and RBF enabled
2. Creating a child transaction that depends on the unconfirmed parent
3. Using RBF to invalidate the entire chain by replacing the parent

## Scripts

### 1. rbf_transaction_chain.py
Uses `python-bitcoinlib` for transaction creation and signing.

### 2. rbf_transaction_rpc.py
Uses raw RPC calls to a Bitcoin node for all operations.

### 3. btc_rbf_gui.py
Complete graphical user interface for the RBF demonstration.

## Prerequisites

1. **Bitcoin Testnet Node**: Running with RPC enabled
2. **Python 3.6+**
3. **Required Python Libraries**:
   - For `rbf_transaction_chain.py`: `python-bitcoinlib`
   - For `rbf_transaction_rpc.py`: `requests`
   - For `btc_rbf_gui.py`: `PyQt5`, `requests`, `python-bitcoinlib`

## Setup Instructions

### 1. Set up Bitcoin Testnet Node

Ensure you have a Bitcoin node running on testnet with RPC enabled. Add these lines to your `bitcoin.conf`:

```
testnet=1
server=1
rpcuser=your_rpc_username
rpcpassword=your_rpc_password
rpcallowip=127.0.0.1
rpcbind=127.0.0.1
```

### 2. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

Alternatively, you can run the setup.bat file on Windows.

### 3. Configure the Scripts

Update the following values in the scripts:
1. **RPC Credentials**: Update username/password in the script
2. **Private Keys/Addresses**: Add your actual testnet private keys and addresses
3. **Amounts**: Adjust transaction amounts as needed

## Running the Scripts

### Option 1: Using python-bitcoinlib

```bash
python rbf_transaction_chain.py
```

### Option 2: Using RPC calls

```bash
python rbf_transaction_rpc.py
```

### Option 3: Using the GUI Application

Double-click `run_gui.bat` or run:

```bash
python btc_rbf_gui.py
```

## How It Works

### Transaction Chain Creation

1. **Parent Transaction**: Created with minimum fee (1 sat/vB) and RBF enabled (sequence: 0xfffffffd)
2. **Child Transaction**: Spends the unconfirmed output of the parent transaction
3. Both transactions are broadcast to the network

### RBF Cancellation (Kill Switch)

1. A new transaction is created spending the same original UTXO
2. This transaction has a much higher fee (50 sat/vB) to ensure replacement
3. When broadcast, it invalidates the parent-child chain

## Understanding the Concepts

### Mempool Ancestry
When a transaction spends an unconfirmed output, it creates a dependency chain in the mempool. The child transaction cannot be confirmed until the parent is confirmed.

### Replace-By-Fee (RBF)
RBF allows replacing an unconfirmed transaction with a new one that pays a higher fee, provided the original transaction signaled RBF capability.

## GUI Application Features

The GUI application provides:

1. **Connection Management**: Easy configuration of Bitcoin node connection
2. **Transaction Creation**: One-click creation of parent-child transaction chains
3. **RBF Cancellation**: "Kill Switch" to invalidate transaction chains
4. **Real-time Feedback**: Progress updates during operations
5. **Complete Logging**: Detailed activity log with timestamps
6. **Results Display**: Clear presentation of transaction IDs and addresses

## Technical Details

### Parent Transaction
- Fee rate: 1 sat/vB (minimum to stay in mempool)
- RBF enabled: sequence=0xfffffffd
- Sends funds from Wallet A to Wallet B (change address)

### Child Transaction
- Fee rate: 20 sat/vB (standard network fee)
- Depends on unconfirmed parent output
- Sends funds from Wallet B to Wallet C (target address)

### Kill Switch (RBF Transaction)
- Fee rate: 50 sat/vB (high fee to ensure replacement)
- Spends same UTXO as parent
- Sends funds back to Wallet A

## Important Notes

1. **Testnet Only**: These scripts are designed for Bitcoin Testnet to avoid losing real funds
2. **Fees**: The fee rates are examples and may need adjustment based on network conditions
3. **Security**: Never use real private keys in test scripts
4. **Node Sync**: Ensure your node is fully synced before running the scripts

## Troubleshooting

### Common Issues

1. **Insufficient Funds**: Make sure your wallet has enough testnet BTC
2. **RPC Connection**: Verify your node is running and RPC credentials are correct
3. **Library Installation**: Ensure all required Python libraries are installed

### Checking Results

You can verify transaction status using:
- `bitcoin-cli getrawtransaction <txid> true`
- Block explorers like https://blockstream.info/testnet/

## License

This code is provided for educational purposes only. Use at your own risk.