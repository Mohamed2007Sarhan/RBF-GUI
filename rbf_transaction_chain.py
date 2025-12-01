#!/usr/bin/env python3
"""
Bitcoin Testnet Transaction Chain with RBF (Replace-By-Fee) Demo

This script demonstrates a Parent-Child transaction dependency chain
and how to invalidate it using RBF.

Author: Senior Blockchain Engineer
"""

import bitcoin
from bitcoin.core import COIN, COutPoint, CTxIn, CTxOut, CTransaction, Hash160, b2x, lx, x
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
import bitcoin.rpc

class BitcoinRBFDemo:
    def __init__(self, private_key_wif, receiver_address):
        """
        Initialize the demo with wallet credentials
        
        Args:
            private_key_wif (str): Private key in WIF format
            receiver_address (str): Target address for child transaction
        """
        # Connect to local Bitcoin node
        self.proxy = bitcoin.rpc.Proxy()
        
        # Parse private key and derive public key/address
        self.private_key = CBitcoinSecret(private_key_wif)
        self.source_address = self.private_key.pub.key_to_address()
        
        # Receiver address
        self.receiver_address = CBitcoinAddress(receiver_address)
        
        # Change address (back to ourselves)
        self.change_address = self.source_address
        
        print(f"Source address: {self.source_address}")
        print(f"Change address: {self.change_address}")
        print(f"Receiver address: {self.receiver_address}")

    def get_utxo(self, min_amount=0.001):
        """
        Find a suitable UTXO to use as input
        
        Args:
            min_amount (float): Minimum amount required in BTC
            
        Returns:
            tuple: (txid, vout, amount) of selected UTXO
        """
        min_satoshis = int(min_amount * COIN)
        
        # Get unspent transaction outputs for our address
        unspent = self.proxy.listunspent()
        
        # Filter for confirmed UTXOs with sufficient amount
        suitable_utxos = [
            utxo for utxo in unspent 
            if utxo['confirmations'] > 0 and utxo['amount'] >= min_satoshis
        ]
        
        if not suitable_utxos:
            raise Exception("No suitable UTXO found with sufficient funds")
            
        # Select the first suitable UTXO
        selected = suitable_utxos[0]
        return (
            selected['txid'], 
            selected['vout'], 
            selected['amount']
        )

    def create_parent_transaction(self, txid, vout, amount, fee_rate=1):
        """
        Create the parent transaction with minimum fee rate
        
        Args:
            txid (bytes): Transaction ID of input UTXO
            vout (int): Output index of input UTXO
            amount (int): Amount in satoshis
            fee_rate (int): Fee rate in sat/vByte (default: 1)
            
        Returns:
            tuple: (signed_tx, txid, vout) of the parent transaction
        """
        # Calculate fees based on estimated size (simple transaction ~190 vBytes)
        fee = fee_rate * 190  # 190 vBytes typical for simple P2PKH transaction
        send_amount = amount - fee
        
        if send_amount <= 0:
            raise Exception("Insufficient funds to cover minimum fee")
        
        # Create transaction inputs
        txin = CTxIn(COutPoint(txid, vout))
        
        # Create transaction outputs (send to change address)
        txout = CTxOut(send_amount, self.change_address.to_scriptPubKey())
        
        # Create unsigned transaction
        tx = CTransaction([txin], [txout])
        
        # Sign transaction
        signed_tx = self.proxy.signrawtransaction(tx)
        
        if not signed_tx['complete']:
            raise Exception("Failed to sign parent transaction")
            
        # Get the TXID of the signed transaction
        txid = signed_tx['tx'].GetTxid()
        
        print(f"Created parent transaction:")
        print(f"  TXID: {b2x(txid)}")
        print(f"  Fee rate: {fee_rate} sat/vByte")
        print(f"  Fee: {fee} satoshis")
        print(f"  Sending: {send_amount} satoshis to {self.change_address}")
        
        return signed_tx['tx'], txid, 0  # vout=0 since it's the first output

    def create_child_transaction(self, parent_txid, parent_vout, amount, network_fee_rate=20):
        """
        Create child transaction spending parent's output
        
        Args:
            parent_txid (bytes): TXID of parent transaction
            parent_vout (int): Output index from parent transaction
            amount (int): Amount in satoshis to send
            network_fee_rate (int): Standard fee rate in sat/vByte
            
        Returns:
            CTransaction: Signed child transaction
        """
        # Calculate fees for child transaction (~190 vBytes)
        fee = network_fee_rate * 190
        send_amount = amount - fee
        
        if send_amount <= 0:
            raise Exception("Insufficient funds to cover network fee")
        
        # Create transaction input (using unconfirmed parent output)
        txin = CTxIn(COutPoint(parent_txid, parent_vout))
        
        # Create transaction output (send to receiver)
        txout = CTxOut(send_amount, self.receiver_address.to_scriptPubKey())
        
        # Create unsigned transaction
        tx = CTransaction([txin], [txout])
        
        # Sign transaction
        signed_tx = self.proxy.signrawtransaction(tx)
        
        if not signed_tx['complete']:
            raise Exception("Failed to sign child transaction")
            
        print(f"Created child transaction:")
        print(f"  TXID: {b2x(signed_tx['tx'].GetTxid())}")
        print(f"  Fee rate: {network_fee_rate} sat/vByte")
        print(f"  Fee: {fee} satoshis")
        print(f"  Sending: {send_amount} satoshis to {self.receiver_address}")
        
        return signed_tx['tx']

    def create_rbf_transaction(self, original_txid, original_vout, amount, rbf_fee_rate=50):
        """
        Create RBF transaction to replace the parent and invalidate the chain
        
        Args:
            original_txid (bytes): TXID of original UTXO
            original_vout (int): Output index of original UTXO
            amount (int): Amount in satoshis
            rbf_fee_rate (int): High fee rate for RBF in sat/vByte
            
        Returns:
            CTransaction: Signed RBF transaction
        """
        # Calculate higher fees for RBF
        fee = rbf_fee_rate * 190  # Still ~190 vBytes
        send_amount = amount - fee
        
        if send_amount <= 0:
            raise Exception("Insufficient funds to cover RBF fee")
        
        # Create transaction input (spending same UTXO as parent)
        txin = CTxIn(COutPoint(original_txid, original_vout))
        
        # Create transaction output (send back to ourselves)
        txout = CTxOut(send_amount, self.source_address.to_scriptPubKey())
        
        # Create unsigned transaction
        tx = CTransaction([txin], [txout])
        
        # Sign transaction
        signed_tx = self.proxy.signrawtransaction(tx)
        
        if not signed_tx['complete']:
            raise Exception("Failed to sign RBF transaction")
            
        print(f"Created RBF transaction:")
        print(f"  TXID: {b2x(signed_tx['tx'].GetTxid())}")
        print(f"  Fee rate: {rbf_fee_rate} sat/vByte")
        print(f"  Fee: {fee} satoshis")
        print(f"  Sending: {send_amount} satoshis back to {self.source_address}")
        
        return signed_tx['tx']

    def execute_transaction_chain(self, amount_btc=0.001):
        """
        Execute the full transaction chain: Parent -> Child
        
        Args:
            amount_btc (float): Amount to send in BTC
        """
        amount_sat = int(amount_btc * COIN)
        
        # Step 1: Find UTXO
        print("\n=== STEP 1: Finding UTXO ===")
        txid, vout, utxo_amount = self.get_utxo(amount_btc * 1.01)  # Slightly more for fees
        print(f"Selected UTXO: {b2x(txid)}:{vout} with {utxo_amount} satoshis")
        
        # Step 2: Create parent transaction
        print("\n=== STEP 2: Creating Parent Transaction ===")
        parent_tx, parent_txid, parent_vout = self.create_parent_transaction(
            lx(b2x(txid)), vout, utxo_amount, fee_rate=1  # Minimum fee rate
        )
        
        # Step 3: Create child transaction
        print("\n=== STEP 3: Creating Child Transaction ===")
        child_tx = self.create_child_transaction(
            parent_txid, parent_vout, utxo_amount, network_fee_rate=20  # Standard fee
        )
        
        # Step 4: Broadcast transactions
        print("\n=== STEP 4: Broadcasting Transactions ===")
        # Broadcast parent first
        parent_txid_hex = self.proxy.sendrawtransaction(parent_tx)
        print(f"Broadcast Parent TX: {b2x(parent_txid_hex)}")
        
        # Broadcast child immediately after
        child_txid_hex = self.proxy.sendrawtransaction(child_tx)
        print(f"Broadcast Child TX: {b2x(child_txid_hex)}")
        
        print("\nTransaction chain created successfully!")
        print(f"Parent TXID: {b2x(parent_txid_hex)}")
        print(f"Child TXID: {b2x(child_txid_hex)}")
        
        return {
            'parent_txid': b2x(parent_txid_hex),
            'child_txid': b2x(child_txid_hex),
            'parent_tx': parent_tx,
            'child_tx': child_tx
        }

    def cancel_parent(self, original_txid, original_vout, amount):
        """
        Cancel the parent transaction using RBF
        
        Args:
            original_txid (bytes): Original UTXO transaction ID
            original_vout (int): Original UTXO output index
            amount (int): Amount in satoshis
        """
        print("\n=== CANCELING PARENT TRANSACTION (RBF) ===")
        
        # Create and broadcast RBF transaction
        rbf_tx = self.create_rbf_transaction(
            original_txid, original_vout, amount, rbf_fee_rate=50  # High fee for RBF
        )
        
        rbf_txid = self.proxy.sendrawtransaction(rbf_tx)
        print(f"Broadcast RBF TX: {b2x(rbf_txid)}")
        
        print("\nRBF transaction broadcast successfully!")
        print("The parent-child chain should now be invalidated.")
        
        return b2x(rbf_txid)


def main():
    """
    Main function demonstrating the transaction chain and RBF
    """
    # Configuration - REPLACE WITH YOUR ACTUAL VALUES
    PRIVATE_KEY_WIF = "cU5NfKJyWz8h76j2nJk2kQk8tM9pP3nN4kK5nN6j7k8nN9pP0qQ1rR2sS3t"  # Testnet WIF
    RECEIVER_ADDRESS = "mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB"  # Testnet address
    
    # Amount to send (in BTC)
    AMOUNT_BTC = 0.001
    
    try:
        # Initialize the demo
        demo = BitcoinRBFDemo(PRIVATE_KEY_WIF, RECEIVER_ADDRESS)
        
        # Execute the transaction chain
        tx_results = demo.execute_transaction_chain(AMOUNT_BTC)
        
        # Wait for user input before cancelling (simulating observation time)
        input("\nPress Enter to trigger RBF cancellation...")
        
        # Cancel the parent transaction using RBF
        # We need to parse the original TXID back to bytes
        original_txid = lx(tx_results['parent_tx'].vin[0].prevout.hash[::-1].hex())
        original_vout = tx_results['parent_tx'].vin[0].prevout.n
        amount = tx_results['parent_tx'].vout[0].nValue
        
        rbf_txid = demo.cancel_parent(original_txid, original_vout, amount)
        
        print(f"\nRBF Transaction ID: {rbf_txid}")
        print("Check your wallet to confirm the chain was invalidated!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. A running Bitcoin Testnet node with RPC enabled")
        print("2. Sufficient funds in your wallet")
        print("3. python-bitcoinlib installed (pip install python-bitcoinlib)")


if __name__ == "__main__":
    main()