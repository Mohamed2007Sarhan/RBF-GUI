#!/usr/bin/env python3
"""
Bitcoin Testnet Transaction Chain with RBF (Replace-By-Fee) Demo - RPC Version

This script demonstrates a Parent-Child transaction dependency chain
and how to invalidate it using RBF using raw RPC calls.

Author: Senior Blockchain Engineer
"""

import json
import requests
from binascii import hexlify, unhexlify

class BitcoinRPC:
    """Simple Bitcoin RPC client"""
    
    def __init__(self, url="http://localhost:18332"):
        """
        Initialize RPC client
        
        Args:
            url (str): RPC endpoint URL
        """
        self.url = url
        # Default auth - REPLACE WITH YOUR ACTUAL RPC CREDENTIALS
        self.auth = ('rpcuser', 'rpcpassword')
        
    def call(self, method, params=[]):
        """
        Make RPC call
        
        Args:
            method (str): RPC method name
            params (list): Method parameters
            
        Returns:
            dict: RPC response
        """
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        
        response = requests.post(
            self.url, 
            json=payload, 
            auth=self.auth,
            headers={'content-type': 'application/json'}
        )
        
        result = response.json()
        if 'error' in result and result['error']:
            raise Exception(f"RPC Error: {result['error']}")
            
        return result['result']

class BitcoinRBFDemoRPC:
    def __init__(self, rpc_url="http://localhost:18332"):
        """
        Initialize the demo with RPC connection
        
        Args:
            rpc_url (str): Bitcoin RPC URL
        """
        self.rpc = BitcoinRPC(rpc_url)
        
    def get_new_address(self, label="", address_type="bech32"):
        """
        Generate a new address
        
        Args:
            label (str): Address label
            address_type (str): Address type
            
        Returns:
            str: New address
        """
        return self.rpc.call("getnewaddress", [label, address_type])
        
    def get_balance(self):
        """
        Get wallet balance
        
        Returns:
            float: Balance in BTC
        """
        return self.rpc.call("getbalance")
        
    def list_unspent(self, min_confirmations=1):
        """
        List unspent transaction outputs
        
        Args:
            min_confirmations (int): Minimum confirmations
            
        Returns:
            list: Unspent outputs
        """
        return self.rpc.call("listunspent", [min_confirmations])
        
    def create_raw_transaction(self, inputs, outputs):
        """
        Create raw transaction
        
        Args:
            inputs (list): Transaction inputs
            outputs (dict): Transaction outputs
            
        Returns:
            str: Hex encoded raw transaction
        """
        return self.rpc.call("createrawtransaction", [inputs, outputs])
        
    def sign_raw_transaction_with_wallet(self, hexstring):
        """
        Sign raw transaction with wallet
        
        Args:
            hexstring (str): Hex encoded transaction
            
        Returns:
            dict: Signed transaction details
        """
        return self.rpc.call("signrawtransactionwithwallet", [hexstring])
        
    def send_raw_transaction(self, hexstring):
        """
        Broadcast raw transaction
        
        Args:
            hexstring (str): Hex encoded transaction
            
        Returns:
            str: Transaction ID
        """
        return self.rpc.call("sendrawtransaction", [hexstring])
        
    def get_raw_transaction(self, txid, verbose=True):
        """
        Get raw transaction details
        
        Args:
            txid (str): Transaction ID
            verbose (bool): Return verbose details
            
        Returns:
            dict: Transaction details
        """
        return self.rpc.call("getrawtransaction", [txid, verbose])

    def create_parent_transaction(self, utxo, to_address, amount_btc, fee_rate=1):
        """
        Create parent transaction with minimum fee
        
        Args:
            utxo (dict): UTXO to spend
            to_address (str): Address to send funds to
            amount_btc (float): Amount to send in BTC
            fee_rate (int): Fee rate in sat/vbyte
            
        Returns:
            dict: Transaction details
        """
        # Estimate transaction size (simple P2WPKH transaction ~110 vbytes)
        tx_size = 110
        fee_satoshi = fee_rate * tx_size
        amount_satoshi = int(amount_btc * 100000000)
        change_amount = amount_satoshi - fee_satoshi
        
        if change_amount <= 0:
            raise Exception("Insufficient funds for fee")
        
        # Create transaction inputs
        inputs = [{
            'txid': utxo['txid'],
            'vout': utxo['vout']
        }]
        
        # Create transaction outputs
        outputs = {
            to_address: change_amount / 100000000.0  # Convert back to BTC
        }
        
        # Create raw transaction
        raw_tx = self.create_raw_transaction(inputs, outputs)
        
        # Sign transaction
        signed_result = self.sign_raw_transaction_with_wallet(raw_tx)
        
        if not signed_result['complete']:
            raise Exception("Failed to sign parent transaction")
            
        return {
            'raw_tx': signed_result['hex'],
            'txid': None,  # Will be set after broadcasting
            'fee_satoshi': fee_satoshi,
            'change_amount': change_amount,
            'size': tx_size
        }

    def create_child_transaction(self, parent_txid, parent_vout, parent_value, 
                               to_address, amount_btc, fee_rate=20):
        """
        Create child transaction spending parent output
        
        Args:
            parent_txid (str): Parent transaction ID
            parent_vout (int): Parent output index
            parent_value (int): Parent output value in satoshi
            to_address (str): Address to send funds to
            amount_btc (float): Amount to send in BTC
            fee_rate (int): Fee rate in sat/vbyte
            
        Returns:
            dict: Transaction details
        """
        # Estimate transaction size (simple P2WPKH transaction ~110 vbytes)
        tx_size = 110
        fee_satoshi = fee_rate * tx_size
        amount_satoshi = int(amount_btc * 100000000)
        change_amount = parent_value - amount_satoshi - fee_satoshi
        
        if change_amount < 0:
            raise Exception("Insufficient funds for child transaction")
        
        # Create transaction inputs
        inputs = [{
            'txid': parent_txid,
            'vout': parent_vout
        }]
        
        # Create transaction outputs
        outputs = {}
        outputs[to_address] = amount_btc
        
        if change_amount > 0:
            # Add change output back to ourselves
            change_addr = self.get_new_address("change")
            outputs[change_addr] = change_amount / 100000000.0
        
        # Create raw transaction
        raw_tx = self.create_raw_transaction(inputs, outputs)
        
        # Sign transaction
        signed_result = self.sign_raw_transaction_with_wallet(raw_tx)
        
        if not signed_result['complete']:
            raise Exception("Failed to sign child transaction")
            
        return {
            'raw_tx': signed_result['hex'],
            'txid': None,  # Will be set after broadcasting
            'fee_satoshi': fee_satoshi,
            'amount_satoshi': amount_satoshi,
            'change_amount': change_amount,
            'size': tx_size
        }

    def create_rbf_transaction(self, original_utxo, to_address, amount_btc, fee_rate=50):
        """
        Create RBF transaction to replace parent
        
        Args:
            original_utxo (dict): Original UTXO to spend
            to_address (str): Address to send funds to
            amount_btc (float): Amount to send in BTC
            fee_rate (int): High fee rate for RBF in sat/vbyte
            
        Returns:
            dict: Transaction details
        """
        # Estimate transaction size (simple P2WPKH transaction ~110 vbytes)
        tx_size = 110
        fee_satoshi = fee_rate * tx_size
        amount_satoshi = int(amount_btc * 100000000)
        change_amount = amount_satoshi - fee_satoshi
        
        if change_amount <= 0:
            raise Exception("Insufficient funds for RBF fee")
        
        # Create transaction inputs
        inputs = [{
            'txid': original_utxo['txid'],
            'vout': original_utxo['vout']
        }]
        
        # Create transaction outputs
        outputs = {
            to_address: change_amount / 100000000.0  # Convert back to BTC
        }
        
        # Create raw transaction
        raw_tx = self.create_raw_transaction(inputs, outputs)
        
        # Sign transaction
        signed_result = self.sign_raw_transaction_with_wallet(raw_tx)
        
        if not signed_result['complete']:
            raise Exception("Failed to sign RBF transaction")
            
        return {
            'raw_tx': signed_result['hex'],
            'txid': None,  # Will be set after broadcasting
            'fee_satoshi': fee_satoshi,
            'change_amount': change_amount,
            'size': tx_size
        }

    def execute_transaction_chain(self, amount_btc=0.001):
        """
        Execute the full transaction chain: Parent -> Child
        
        Args:
            amount_btc (float): Amount to send in BTC
        """
        print("=== BITCOIN TESTNET RBF DEMONSTRATION ===")
        
        # Get wallet info
        balance = self.get_balance()
        print(f"Wallet balance: {balance} BTC")
        
        if balance < amount_btc * 1.1:  # Need some extra for fees
            raise Exception("Insufficient funds in wallet")
        
        # Get a suitable UTXO
        unspent = self.list_unspent(1)  # Confirmed UTXOs only
        if not unspent:
            raise Exception("No confirmed UTXOs found")
            
        # Select UTXO with sufficient funds
        selected_utxo = None
        required_amount = int(amount_btc * 1.1 * 100000000)  # 10% extra for fees
        for utxo in unspent:
            if utxo['amount'] * 100000000 >= required_amount:
                selected_utxo = utxo
                break
                
        if not selected_utxo:
            raise Exception("No UTXO with sufficient funds found")
            
        print(f"Selected UTXO: {selected_utxo['txid']}:{selected_utxo['vout']}")
        print(f"UTXO Amount: {selected_utxo['amount']} BTC")
        
        # Generate addresses
        change_address = self.get_new_address("parent_change")
        receiver_address = self.get_new_address("receiver")
        rbf_address = self.get_new_address("rbf_return")
        
        print(f"Change address: {change_address}")
        print(f"Receiver address: {receiver_address}")
        print(f"RBF return address: {rbf_address}")
        
        # Step 1: Create parent transaction (minimum fee)
        print("\n=== CREATING PARENT TRANSACTION ===")
        parent_tx = self.create_parent_transaction(
            selected_utxo, change_address, amount_btc, fee_rate=1
        )
        print(f"Parent transaction created")
        print(f"  Fee: {parent_tx['fee_satoshi']} satoshis ({parent_tx['fee_satoshi']/parent_tx['size']} sat/vB)")
        print(f"  Size: {parent_tx['size']} vbytes")
        
        # Step 2: Create child transaction
        print("\n=== CREATING CHILD TRANSACTION ===")
        # For child transaction, we need to decode the parent to get output value
        child_tx = self.create_child_transaction(
            "temp_txid", 0, parent_tx['change_amount'] + parent_tx['fee_satoshi'],
            receiver_address, amount_btc * 0.5, fee_rate=20  # Send half amount
        )
        print(f"Child transaction created")
        print(f"  Amount: {child_tx['amount_satoshi']} satoshis")
        print(f"  Fee: {child_tx['fee_satoshi']} satoshis ({child_tx['fee_satoshi']/child_tx['size']} sat/vB)")
        print(f"  Size: {child_tx['size']} vbytes")
        
        # Step 3: Broadcast parent transaction
        print("\n=== BROADCASTING PARENT TRANSACTION ===")
        parent_txid = self.send_raw_transaction(parent_tx['raw_tx'])
        parent_tx['txid'] = parent_txid
        print(f"Parent transaction broadcast: {parent_txid}")
        
        # Update child transaction with actual parent txid and vout
        child_tx = self.create_child_transaction(
            parent_txid, 0, parent_tx['change_amount'] + parent_tx['fee_satoshi'],
            receiver_address, amount_btc * 0.5, fee_rate=20
        )
        
        # Step 4: Broadcast child transaction
        print("\n=== BROADCASTING CHILD TRANSACTION ===")
        child_txid = self.send_raw_transaction(child_tx['raw_tx'])
        child_tx['txid'] = child_txid
        print(f"Child transaction broadcast: {child_txid}")
        
        print("\n=== TRANSACTION CHAIN CREATED ===")
        print(f"Parent TXID: {parent_txid}")
        print(f"Child TXID: {child_txid}")
        
        return {
            'parent_txid': parent_txid,
            'child_txid': child_txid,
            'parent_tx': parent_tx,
            'child_tx': child_tx,
            'original_utxo': selected_utxo,
            'rbf_address': rbf_address
        }

    def cancel_with_rbf(self, original_utxo, rbf_address, amount_btc):
        """
        Cancel the transaction chain using RBF
        
        Args:
            original_utxo (dict): Original UTXO
            rbf_address (str): Address to send funds to
            amount_btc (float): Amount in BTC
        """
        print("\n=== CREATING RBF TRANSACTION ===")
        
        # Create RBF transaction with high fee
        rbf_tx = self.create_rbf_transaction(
            original_utxo, rbf_address, amount_btc, fee_rate=50  # High fee for RBF
        )
        print(f"RBF transaction created")
        print(f"  Fee: {rbf_tx['fee_satoshi']} satoshis ({rbf_tx['fee_satoshi']/rbf_tx['size']} sat/vB)")
        print(f"  Size: {rbf_tx['size']} vbytes")
        
        # Broadcast RBF transaction
        print("\n=== BROADCASTING RBF TRANSACTION ===")
        rbf_txid = self.send_raw_transaction(rbf_tx['raw_tx'])
        rbf_tx['txid'] = rbf_txid
        print(f"RBF transaction broadcast: {rbf_txid}")
        
        print("\n=== RBF COMPLETED ===")
        print("The original transaction chain should now be invalidated!")
        print(f"RBF TXID: {rbf_txid}")
        
        return rbf_txid

def main():
    """
    Main function demonstrating the RBF transaction chain
    """
    try:
        # Initialize the demo
        # Make sure to update with your node's RPC credentials
        demo = BitcoinRBFDemoRPC("http://localhost:18332")
        
        # Execute the transaction chain
        results = demo.execute_transaction_chain(0.001)  # 0.001 BTC
        
        # Wait for user input before performing RBF
        input("\nPress Enter to perform RBF cancellation...")
        
        # Perform RBF to cancel the chain
        rbf_txid = demo.cancel_with_rbf(
            results['original_utxo'],
            results['rbf_address'],
            0.001
        )
        
        print(f"\nFinal RBF transaction: {rbf_txid}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo run this script, you need:")
        print("1. A running Bitcoin Testnet node with RPC enabled")
        print("2. Sufficient funds in your wallet")
        print("3. Update the RPC credentials in the BitcoinRPC class")
        print("4. Install requests library: pip install requests")

if __name__ == "__main__":
    main()