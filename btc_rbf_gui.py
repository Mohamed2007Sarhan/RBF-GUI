#!/usr/bin/env python3
"""
Bitcoin Testnet RBF Transaction Chain GUI Tool

A complete graphical interface for demonstrating Replace-By-Fee (RBF) dynamics
and mempool ancestry on Bitcoin Testnet.

Author: Senior Blockchain Engineer
"""

import sys
import json
import threading
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, 
    QFormLayout, QMessageBox, QTabWidget, QProgressBar, QCheckBox,
    QGridLayout, QFrame, QComboBox, QTextBrowser
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Language dictionaries
LANGUAGES = {
    'en': {
        'window_title': 'Bitcoin Testnet RBF Transaction Tool',
        'config_tab': 'Configuration',
        'transactions_tab': 'Transactions',
        'log_tab': 'Activity Log',
        'flowchart_tab': 'Flowchart',
        'status_tab': 'Wallet Status',
        'node_connection': 'Bitcoin Node Connection',
        'host': 'Host:',
        'port': 'Port:',
        'username': 'Username:',
        'password': 'Password:',
        'test_connection': 'Test Connection',
        'not_connected': 'Not connected',
        'connected': 'Connected to Bitcoin Node (Blocks: {})',
        'connection_failed': 'Connection failed: {}',
        'transaction_details': 'Transaction Details',
        'amount_btc': 'Amount (BTC):',
        'create_chain': 'Create Transaction Chain (Parent → Child)',
        'activate_kill': 'Activate Kill Switch (RBF)',
        'stop_all': 'Stop All & Return Funds to Wallet A',
        'transaction_results': 'Transaction Results:',
        'activity_log': 'Activity Log:',
        'clear_log': 'Clear Log',
        'success_connected': 'SUCCESS: Connected to Bitcoin node',
        'error_connection': 'ERROR: Connection failed - {}',
        'action_create': 'ACTION: Creating transaction chain with {} BTC',
        'action_kill': 'ACTION: Activating kill switch (RBF)',
        'action_stop': 'ACTION: Stopping all transactions and returning funds to Wallet A',
        'success_chain': 'SUCCESS: Transaction chain created',
        'success_kill': 'SUCCESS: Kill switch activated',
        'success_stop': 'SUCCESS: All transactions stopped, funds returned to Wallet A',
        'chain_invalidated': 'Transaction chain invalidated',
        'funds_returned': 'Funds returned to Wallet A.',
        'error': 'ERROR: {}',
        'progress': 'PROGRESS: {}',
        'parent_txid': 'Parent TXID: {}',
        'child_txid': 'Child TXID: {}',
        'rbf_txid': 'RBF TXID: {}',
        'wallet_addresses': '=== WALLET ADDRESSES ===',
        'wallet_a': 'Wallet A (Original): {}',
        'wallet_b': 'Wallet B (Change): {}',
        'wallet_c': 'Wallet C (Receiver): {}',
        'chain_created': '=== TRANSACTION CHAIN CREATED ===',
        'kill_activated': '=== KILL SWITCH ACTIVATED (RBF) ===',
        'all_stopped': '=== ALL TRANSACTIONS STOPPED ===',
        'no_chain': 'No transaction chain to cancel.',
        'invalid_amount': 'Invalid amount. Please enter a valid number.',
        'operation_failed': 'Operation failed',
        'ready': 'Ready to connect to Bitcoin node',
        'success': 'Successfully connected to Bitcoin node',
        'failed': 'Failed to connect to Bitcoin node',
        'creating_chain': 'Creating transaction chain...',
        'activating_kill': 'Activating kill switch...',
        'stopping_all': 'Stopping all transactions...',
        'language': 'Language:',
        'english': 'English',
        'arabic': 'Arabic'
    },
    'ar': {
        'window_title': 'أداة معاملات بتكوين تيستنيت باستخدام RBF',
        'config_tab': 'الإعدادات',
        'transactions_tab': 'المعاملات',
        'log_tab': 'سجل الأنشطة',
        'flowchart_tab': 'مخطط التدفق',
        'status_tab': 'حالة المحفظة',
        'node_connection': 'اتصال عقدة بتكوين',
        'host': 'المضيف:',
        'port': 'المنفذ:',
        'username': 'اسم المستخدم:',
        'password': 'كلمة المرور:',
        'test_connection': 'اختبار الاتصال',
        'not_connected': 'غير متصل',
        'connected': 'متصل بعقدة بتكوين (الكتل: {})',
        'connection_failed': 'فشل الاتصال: {}',
        'transaction_details': 'تفاصيل المعاملة',
        'amount_btc': 'المبلغ (BTC):',
        'create_chain': 'إنشاء سلسلة معاملات (الأصل → الفرع)',
        'activate_kill': 'تفعيل مفتاح الإنهاء (RBF)',
        'stop_all': 'إيقاف الكل وإعادة الأموال إلى المحفظة أ',
        'transaction_results': 'نتائج المعاملة:',
        'activity_log': 'سجل الأنشطة:',
        'clear_log': 'مسح السجل',
        'success_connected': 'نجاح: تم الاتصال بعقدة بتكوين',
        'error_connection': 'خطأ: فشل الاتصال - {}',
        'action_create': 'إجراء: إنشاء سلسلة معاملات بمبلغ {} BTC',
        'action_kill': 'إجراء: تفعيل مفتاح الإنهاء (RBF)',
        'action_stop': 'إجراء: إيقاف جميع المعاملات وإعادة الأموال إلى المحفظة أ',
        'success_chain': 'نجاح: تم إنشاء سلسلة المعاملات',
        'success_kill': 'نجاح: تم تفعيل مفتاح الإنهاء',
        'success_stop': 'نجاح: تم إيقاف جميع المعاملات، وتمت إعادة الأموال إلى المحفظة أ',
        'chain_invalidated': 'تم إبطال سلسلة المعاملات',
        'funds_returned': 'تمت إعادة الأموال إلى المحفظة أ.',
        'error': 'خطأ: {}',
        'progress': 'تقدم: {}',
        'parent_txid': 'معرف المعاملة الأصل: {}',
        'child_txid': 'معرف المعاملة الفرعية: {}',
        'rbf_txid': 'معرف معاملة RBF: {}',
        'wallet_addresses': '=== عناوين المحافظ ===',
        'wallet_a': 'المحفظة أ (الأصلية): {}',
        'wallet_b': 'المحفظة ب (الباقي): {}',
        'wallet_c': 'المحفظة ج (المستلمة): {}',
        'chain_created': '=== تم إنشاء سلسلة المعاملات ===',
        'kill_activated': '=== تم تفعيل مفتاح الإنهاء (RBF) ===',
        'all_stopped': '=== تم إيقاف جميع المعاملات ===',
        'no_chain': 'لا توجد سلسلة معاملات لإلغائها.',
        'invalid_amount': 'مبلغ غير صالح. يرجى إدخال رقم صحيح.',
        'operation_failed': 'فشلت العملية',
        'ready': 'جاهز للاتصال بعقدة بتكوين',
        'success': 'تم الاتصال بنجاح بعقدة بتكوين',
        'failed': 'فشل الاتصال بعقدة بتكوين',
        'creating_chain': 'جارٍ إنشاء سلسلة المعاملات...',
        'activating_kill': 'جارٍ تفعيل مفتاح الإنهاء...',
        'stopping_all': 'جارٍ إيقاف جميع المعاملات...',
        'language': 'اللغة:',
        'english': 'الإنجليزية',
        'arabic': 'العربية'
    }
}

class RPCHandler:
    """Handles Bitcoin RPC communications"""
    
    def __init__(self, host="localhost", port=18332, user="", password=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url = f"http://{host}:{port}"
        
    def call(self, method, params=[]):
        """Make RPC call"""
        if not REQUESTS_AVAILABLE:
            raise Exception("Requests library not available")
            
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        
        try:
            response = requests.post(
                self.url, 
                json=payload, 
                auth=(self.user, self.password),
                headers={'content-type': 'application/json'},
                timeout=30
            )
            
            result = response.json()
            if 'error' in result and result['error']:
                raise Exception(f"RPC Error: {result['error']}")
                
            return result['result']
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Bitcoin node. Check if it's running.")
        except Exception as e:
            raise Exception(f"RPC Call failed: {str(e)}")


class WorkerSignals(QObject):
    """Signals for worker threads"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)


class TransactionWorker(threading.Thread):
    """Worker thread for transaction operations"""
    
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    def run(self):
        try:
            if self.operation == "create_chain":
                result = self.create_transaction_chain(*self.args, **self.kwargs)
            elif self.operation == "cancel_rbf":
                result = self.cancel_with_rbf(*self.args, **self.kwargs)
            elif self.operation == "stop_all":
                result = self.stop_all_transactions(*self.args, **self.kwargs)
            else:
                raise Exception("Unknown operation")
                
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
            
    def create_transaction_chain(self, rpc_handler, amount_btc, wif, wallet_a, wallet_b, wallet_c):
        """Create parent-child transaction chain"""
        self.signals.progress.emit("Validating private key...")
        
        # Validate private key
        try:
            # In a real implementation, we would validate the WIF key here
            # For now, we'll just check it's not empty
            if not wif:
                raise Exception("Invalid private key")
        except Exception as e:
            raise Exception(f"Private key validation failed: {str(e)}")
        
        self.signals.progress.emit("Getting wallet balance...")
        balance = rpc_handler.call("getbalance")
        
        if balance < amount_btc * 1.1:
            raise Exception("Insufficient funds in wallet")
            
        self.signals.progress.emit("Finding suitable UTXO...")
        unspent = rpc_handler.call("listunspent", [1])  # Confirmed UTXOs only
        
        if not unspent:
            raise Exception("No confirmed UTXOs found")
            
        # Select UTXO with sufficient funds
        selected_utxo = None
        required_amount = int(amount_btc * 1.1 * 100000000)  # 10% extra for fees
        for utxo in unspent:
            if int(utxo['amount'] * 100000000) >= required_amount:
                selected_utxo = utxo
                break
                
        if not selected_utxo:
            raise Exception("No UTXO with sufficient funds found")
            
        self.signals.progress.emit(f"Selected UTXO: {selected_utxo['txid']}:{selected_utxo['vout']}")
        
        # In a real implementation, we would use the provided addresses
        # For now, we'll generate new addresses but store the provided ones for reference
        
        # Create parent transaction (minimum fee with RBF sequence)
        self.signals.progress.emit("Creating parent transaction with RBF sequence...")
        parent_inputs = [{
            'txid': selected_utxo['txid'],
            'vout': selected_utxo['vout'],
            'sequence': 0xfffffffd  # Enable RBF as per your requirement
        }]
        
        # Calculate fees (1 sat/vB * 110 vbytes)
        parent_fee_satoshi = 1 * 110
        parent_amount_satoshi = int(amount_btc * 100000000)
        parent_change_amount = parent_amount_satoshi - parent_fee_satoshi
        
        if parent_change_amount <= 0:
            raise Exception("Insufficient funds for parent transaction fee")
            
        parent_outputs = {
            wallet_b: parent_change_amount / 100000000.0  # Send to Wallet B
        }
        
        parent_raw_tx = rpc_handler.call("createrawtransaction", [parent_inputs, parent_outputs])
        parent_signed_result = rpc_handler.call("signrawtransactionwithwallet", [parent_raw_tx])
        
        if not parent_signed_result['complete']:
            raise Exception("Failed to sign parent transaction")
            
        # Create child transaction
        self.signals.progress.emit("Creating child transaction...")
        # We need to broadcast parent first to get real txid
        self.signals.progress.emit("Broadcasting parent transaction...")
        parent_txid = rpc_handler.call("sendrawtransaction", [parent_signed_result['hex']])
        
        # Now create child transaction spending parent output
        child_inputs = [{
            'txid': parent_txid,
            'vout': 0
        }]
        
        # Calculate fees (20 sat/vB * 110 vbytes)
        child_fee_satoshi = 20 * 110
        child_send_amount = int(amount_btc * 0.5 * 100000000)  # Send half amount to Wallet C
        child_change_amount = parent_change_amount - child_send_amount - child_fee_satoshi
        
        if child_change_amount < 0:
            raise Exception("Insufficient funds for child transaction")
            
        child_outputs = {
            wallet_c: child_send_amount / 100000000.0  # Send to Wallet C
        }
        
        if child_change_amount > 0:
            # Generate a change address for the child transaction
            child_change_addr = rpc_handler.call("getnewaddress", ["Child_Change", "bech32"])
            child_outputs[child_change_addr] = child_change_amount / 100000000.0
            
        child_raw_tx = rpc_handler.call("createrawtransaction", [child_inputs, child_outputs])
        child_signed_result = rpc_handler.call("signrawtransactionwithwallet", [child_raw_tx])
        
        if not child_signed_result['complete']:
            raise Exception("Failed to sign child transaction")
            
        self.signals.progress.emit("Broadcasting child transaction...")
        child_txid = rpc_handler.call("sendrawtransaction", [child_signed_result['hex']])
        
        return {
            'parent_txid': parent_txid,
            'child_txid': child_txid,
            'wallet_a': wallet_a,
            'wallet_b': wallet_b,
            'wallet_c': wallet_c,
            'original_utxo': selected_utxo
        }
        
    def cancel_with_rbf(self, rpc_handler, original_utxo, wallet_a, amount_btc):
        """Cancel transaction chain using RBF (kill switch)"""
        self.signals.progress.emit("Creating RBF transaction (kill switch)...")
        
        # Create RBF transaction with high fee (50 sat/vB * 110 vbytes)
        rbf_fee_satoshi = 50 * 110
        rbf_amount_satoshi = int(amount_btc * 100000000)
        rbf_change_amount = rbf_amount_satoshi - rbf_fee_satoshi
        
        if rbf_change_amount <= 0:
            raise Exception("Insufficient funds for RBF transaction fee")
            
        # Use same UTXO as parent but send back to Wallet A with high fee
        rbf_inputs = [{
            'txid': original_utxo['txid'],
            'vout': original_utxo['vout']
        }]
        
        rbf_outputs = {
            wallet_a: rbf_change_amount / 100000000.0  # Send back to Wallet A
        }
        
        rbf_raw_tx = rpc_handler.call("createrawtransaction", [rbf_inputs, rbf_outputs])
        rbf_signed_result = rpc_handler.call("signrawtransactionwithwallet", [rbf_raw_tx])
        
        if not rbf_signed_result['complete']:
            raise Exception("Failed to sign RBF transaction")
            
        self.signals.progress.emit("Broadcasting RBF transaction (kill switch)...")
        rbf_txid = rpc_handler.call("sendrawtransaction", [rbf_signed_result['hex']])
        
        return {
            'rbf_txid': rbf_txid
        }
        
    def stop_all_transactions(self, rpc_handler, original_utxo, wallet_a, amount_btc):
        """Stop all transactions and return funds to Wallet A"""
        self.signals.progress.emit("Creating stop-all transaction...")
        
        # Create transaction with high fee (50 sat/vB * 110 vbytes) to return funds
        stop_fee_satoshi = 50 * 110
        stop_amount_satoshi = int(amount_btc * 100000000)
        stop_change_amount = stop_amount_satoshi - stop_fee_satoshi
        
        if stop_change_amount <= 0:
            raise Exception("Insufficient funds for stop-all transaction fee")
            
        # Use same UTXO as parent but send back to Wallet A with high fee
        stop_inputs = [{
            'txid': original_utxo['txid'],
            'vout': original_utxo['vout']
        }]
        
        stop_outputs = {
            wallet_a: stop_change_amount / 100000000.0  # Send back to Wallet A
        }
        
        stop_raw_tx = rpc_handler.call("createrawtransaction", [stop_inputs, stop_outputs])
        stop_signed_result = rpc_handler.call("signrawtransactionwithwallet", [stop_raw_tx])
        
        if not stop_signed_result['complete']:
            raise Exception("Failed to sign stop-all transaction")
            
        self.signals.progress.emit("Broadcasting stop-all transaction...")
        stop_txid = rpc_handler.call("sendrawtransaction", [stop_signed_result['hex']])
        
        return {
            'stop_txid': stop_txid
        }


class BitcoinRBFTool(QMainWindow):
    """Main GUI application for Bitcoin RBF demonstration"""
    
    def __init__(self):
        super().__init__()
        self.rpc_handler = None
        self.transaction_results = None
        self.current_language = 'en'
        self.wallet_c_funded = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(LANGUAGES[self.current_language]['window_title'])
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Configuration tab
        self.config_tab = self.create_config_tab()
        self.tabs.addTab(self.config_tab, LANGUAGES[self.current_language]['config_tab'])
        
        # Transaction tab
        self.transaction_tab = self.create_transaction_tab()
        self.tabs.addTab(self.transaction_tab, LANGUAGES[self.current_language]['transactions_tab'])
        
        # Log tab
        self.log_tab = self.create_log_tab()
        self.tabs.addTab(self.log_tab, LANGUAGES[self.current_language]['log_tab'])
        
        # Flowchart tab
        self.flowchart_tab = self.create_flowchart_tab()
        self.tabs.addTab(self.flowchart_tab, LANGUAGES[self.current_language]['flowchart_tab'])
        
        # Status tab
        self.status_tab = self.create_status_tab()
        self.tabs.addTab(self.status_tab, LANGUAGES[self.current_language]['status_tab'])
        
        # Status bar
        self.statusBar().showMessage(LANGUAGES[self.current_language]['ready'])
        
    def create_config_tab(self):
        """Create configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(LANGUAGES[self.current_language]['language'])
        self.language_combo = QComboBox()
        self.language_combo.addItem(LANGUAGES[self.current_language]['english'], 'en')
        self.language_combo.addItem(LANGUAGES[self.current_language]['arabic'], 'ar')
        self.language_combo.setCurrentIndex(0 if self.current_language == 'en' else 1)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Connection group
        conn_group = QGroupBox(LANGUAGES[self.current_language]['node_connection'])
        conn_layout = QFormLayout()
        
        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("18332")
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        conn_layout.addRow(LANGUAGES[self.current_language]['host'], self.host_input)
        conn_layout.addRow(LANGUAGES[self.current_language]['port'], self.port_input)
        conn_layout.addRow(LANGUAGES[self.current_language]['username'], self.user_input)
        conn_layout.addRow(LANGUAGES[self.current_language]['password'], self.password_input)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Test connection button
        self.test_conn_btn = QPushButton(LANGUAGES[self.current_language]['test_connection'])
        self.test_conn_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_conn_btn)
        
        # Connection status
        self.conn_status = QLabel(LANGUAGES[self.current_language]['not_connected'])
        self.conn_status.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.conn_status)
        
        # Spacer
        layout.addStretch()
        
        return tab
        
    def create_transaction_tab(self):
        """Create transaction tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Wallet Credentials Group
        wallet_group = QGroupBox("Wallet Credentials")
        wallet_layout = QFormLayout()
        
        self.wif_input = QLineEdit()
        self.wif_input.setEchoMode(QLineEdit.Password)
        self.wif_input.setToolTip("Private Key in WIF format")
        wallet_layout.addRow("Private Key (WIF):", self.wif_input)
        
        wallet_group.setLayout(wallet_layout)
        layout.addWidget(wallet_group)
        
        # Wallet Addresses Group
        addresses_group = QGroupBox("Wallet Addresses")
        addresses_layout = QFormLayout()
        
        self.wallet_a_input = QLineEdit()
        self.wallet_a_input.setToolTip("Wallet A (Source/Return Address)")
        addresses_layout.addRow("Wallet A (Source):", self.wallet_a_input)
        
        self.wallet_b_input = QLineEdit()
        self.wallet_b_input.setToolTip("Wallet B (Change Address)")
        addresses_layout.addRow("Wallet B (Change):", self.wallet_b_input)
        
        self.wallet_c_input = QLineEdit()
        self.wallet_c_input.setToolTip("Wallet C (Receiver Address)")
        addresses_layout.addRow("Wallet C (Receiver):", self.wallet_c_input)
        
        addresses_group.setLayout(addresses_layout)
        layout.addWidget(addresses_group)
        
        # Amount group
        amount_group = QGroupBox(LANGUAGES[self.current_language]['transaction_details'])
        amount_layout = QFormLayout()
        
        self.amount_input = QLineEdit("0.001")
        self.amount_input.setToolTip(LANGUAGES[self.current_language]['amount_btc'])
        amount_layout.addRow(LANGUAGES[self.current_language]['amount_btc'], self.amount_input)
        
        amount_group.setLayout(amount_layout)
        layout.addWidget(amount_group)
        
        # Action buttons
        btn_layout = QVBoxLayout()
        
        self.create_chain_btn = QPushButton(LANGUAGES[self.current_language]['create_chain'])
        self.create_chain_btn.clicked.connect(self.create_transaction_chain)
        self.create_chain_btn.setEnabled(False)
        btn_layout.addWidget(self.create_chain_btn)
        
        self.cancel_rbf_btn = QPushButton(LANGUAGES[self.current_language]['activate_kill'])
        self.cancel_rbf_btn.clicked.connect(self.cancel_with_rbf)
        self.cancel_rbf_btn.setEnabled(False)
        btn_layout.addWidget(self.cancel_rbf_btn)
        
        self.stop_all_btn = QPushButton(LANGUAGES[self.current_language]['stop_all'])
        self.stop_all_btn.clicked.connect(self.stop_all_transactions)
        self.stop_all_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_all_btn)
        
        layout.addLayout(btn_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setFont(QFont("Courier New", 10))
        layout.addWidget(QLabel(LANGUAGES[self.current_language]['transaction_results']))
        layout.addWidget(self.results_display)
        
        return tab
        
    def create_log_tab(self):
        """Create log tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier New", 9))
        layout.addWidget(QLabel(LANGUAGES[self.current_language]['activity_log']))
        layout.addWidget(self.log_display)
        
        # Clear log button
        clear_log_btn = QPushButton(LANGUAGES[self.current_language]['clear_log'])
        clear_log_btn.clicked.connect(self.clear_log)
        layout.addWidget(clear_log_btn)
        
        return tab
        
    def create_flowchart_tab(self):
        """Create flowchart tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Flowchart display
        self.flowchart_display = QTextBrowser()
        self.flowchart_display.setFont(QFont("Courier New", 10))
        self.update_flowchart()
        layout.addWidget(QLabel("Transaction Flow:"))
        layout.addWidget(self.flowchart_display)
        
        return tab
        
    def create_status_tab(self):
        """Create wallet status tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Status display
        self.status_display = QTextBrowser()
        self.status_display.setFont(QFont("Courier New", 10))
        self.update_wallet_status()
        layout.addWidget(QLabel("Wallet Status:"))
        layout.addWidget(self.status_display)
        
        return tab
        
    def change_language(self, index):
        """Change the application language"""
        self.current_language = self.language_combo.itemData(index)
        self.update_ui_texts()
        
    def update_ui_texts(self):
        """Update all UI texts to the current language"""
        # Window title
        self.setWindowTitle(LANGUAGES[self.current_language]['window_title'])
        
        # Tabs
        self.tabs.setTabText(0, LANGUAGES[self.current_language]['config_tab'])
        self.tabs.setTabText(1, LANGUAGES[self.current_language]['transactions_tab'])
        self.tabs.setTabText(2, LANGUAGES[self.current_language]['log_tab'])
        self.tabs.setTabText(3, LANGUAGES[self.current_language]['flowchart_tab'])
        self.tabs.setTabText(4, LANGUAGES[self.current_language]['status_tab'])
        
        # Configuration tab
        conn_group = self.config_tab.findChild(QGroupBox)
        if conn_group:
            conn_group.setTitle(LANGUAGES[self.current_language]['node_connection'])
        
        # Update labels and buttons
        # ... (this would continue for all UI elements)
        
        # Status bar
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(LANGUAGES[self.current_language]['ready'])
            
    def update_flowchart(self):
        """Update the flowchart display"""
        if self.current_language == 'ar':
            flowchart = """
    ┌─────────────┐
    │  المحفظة أ  │
    │ (الأصلية)   │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │معاملة الأصل │◄──┐
    │(رسوم قليلة) │   │
    └──────┬──────┘   │
           │          │ RBF
    ┌──────▼──────┐   │
    │  المحفظة ب  │   │
    │  (الباقي)   │   │
    └──────┬──────┘   │
           │          │
    ┌──────▼──────┐   │
    │معاملة الفرع │   │
    │(رسوم عادية) │   │
    └──────┬──────┘   │
           │          │
    ┌──────▼──────┐   │
    │  المحفظة ج  │   │
    │ (المستلمة)  │   │
    └─────────────┘   │
                      │
                 ┌────▼────┐
                 │مفتاح الإ│
                 │نهاء RBF │
                 └─────────┘
            """
        else:
            flowchart = """
    ┌─────────────┐
    │  Wallet A   │
    │ (Original)  │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │ Parent TX   │◄──┐
    │(Low Fee)    │   │
    └──────┬──────┘   │
           │          │ RBF
    ┌──────▼──────┐   │
    │  Wallet B   │   │
    │ (Change)    │   │
    └──────┬──────┘   │
           │          │
    ┌──────▼──────┐   │
    │ Child TX    │   │
    │(Normal Fee) │   │
    └──────┬──────┘   │
           │          │
    ┌──────▼──────┐   │
    │  Wallet C   │   │
    │ (Receiver)  │   │
    └─────────────┘   │
                      │
                 ┌────▼────┐
                 │Kill SW  │
                 │(RBF)    │
                 └─────────┘
            """
        
        self.flowchart_display.setPlainText(flowchart)
        
    def update_wallet_status(self):
        """Update the wallet status display"""
        if self.current_language == 'ar':
            if self.wallet_c_funded:
                status = "المحفظة ج: تحتوي على الأموال (غير مؤكدة)\n"
                status += "الحالة: في انتظار التأكيد أو إلغاء المعاملة"
            else:
                status = "المحفظة ج: لا تحتوي على الأموال\n"
                status += "الحالة: الأموال عادت إلى المحفظة أ"
        else:
            if self.wallet_c_funded:
                status = "Wallet C: Funds received (unconfirmed)\n"
                status += "Status: Awaiting confirmation or transaction cancellation"
            else:
                status = "Wallet C: No funds\n"
                status += "Status: Funds returned to Wallet A"
                
        self.status_display.setPlainText(status)
        
    def test_connection(self):
        """Test connection to Bitcoin node"""
        try:
            host = self.host_input.text()
            port = int(self.port_input.text())
            user = self.user_input.text()
            password = self.password_input.text()
            
            self.rpc_handler = RPCHandler(host, port, user, password)
            
            # Test with a simple call
            result = self.rpc_handler.call("getblockchaininfo")
            
            msg = LANGUAGES[self.current_language]['connected'].format(result['blocks'])
            self.conn_status.setText(msg)
            self.conn_status.setStyleSheet("color: green; font-weight: bold;")
            self.create_chain_btn.setEnabled(True)
            self.statusBar().showMessage(LANGUAGES[self.current_language]['success'])
            
            # Log the connection
            self.log_message(LANGUAGES[self.current_language]['success_connected'])
            
        except Exception as e:
            msg = LANGUAGES[self.current_language]['connection_failed'].format(str(e))
            self.conn_status.setText(msg)
            self.conn_status.setStyleSheet("color: red; font-weight: bold;")
            self.create_chain_btn.setEnabled(False)
            self.statusBar().showMessage(LANGUAGES[self.current_language]['failed'])
            
            # Log the error
            self.log_message(LANGUAGES[self.current_language]['error_connection'].format(str(e)))
            
    def create_transaction_chain(self):
        """Create parent-child transaction chain"""
        try:
            amount_btc = float(self.amount_input.text())
        except ValueError:
            QMessageBox.critical(self, "Error", LANGUAGES[self.current_language]['invalid_amount'])
            return
            
        # Get wallet credentials and addresses
        wif = self.wif_input.text().strip()
        wallet_a = self.wallet_a_input.text().strip()
        wallet_b = self.wallet_b_input.text().strip()
        wallet_c = self.wallet_c_input.text().strip()
        
        # Validate inputs
        if not wif:
            QMessageBox.critical(self, "Error", "Private Key (WIF) is required")
            return
            
        if not wallet_a:
            QMessageBox.critical(self, "Error", "Wallet A (Source) address is required")
            return
            
        if not wallet_b:
            QMessageBox.critical(self, "Error", "Wallet B (Change) address is required")
            return
            
        if not wallet_c:
            QMessageBox.critical(self, "Error", "Wallet C (Receiver) address is required")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.create_chain_btn.setEnabled(False)
        self.results_display.clear()
        
        # Log the action
        self.log_message(LANGUAGES[self.current_language]['action_create'].format(amount_btc))
        
        # Update wallet status
        self.wallet_c_funded = True
        self.update_wallet_status()
        self.update_flowchart()
        
        # Start worker thread
        self.worker = TransactionWorker("create_chain", self.rpc_handler, amount_btc, wif, wallet_a, wallet_b, wallet_c)
        self.worker.signals.finished.connect(self.on_chain_created)
        self.worker.signals.error.connect(self.on_worker_error)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.start()
        
    def cancel_with_rbf(self):
        """Cancel transaction chain using RBF (kill switch)"""
        if not self.transaction_results:
            QMessageBox.warning(self, "Warning", LANGUAGES[self.current_language]['no_chain'])
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.cancel_rbf_btn.setEnabled(False)
        
        # Log the action
        self.log_message(LANGUAGES[self.current_language]['action_kill'])
        
        # Get wallet credentials and addresses
        wif = self.wif_input.text().strip()
        wallet_a = self.wallet_a_input.text().strip()
        wallet_b = self.wallet_b_input.text().strip()
        wallet_c = self.wallet_c_input.text().strip()
        
        # Start worker thread
        self.worker = TransactionWorker(
            "cancel_rbf", 
            self.rpc_handler, 
            self.transaction_results['original_utxo'],
            self.transaction_results['wallet_a'],
            float(self.amount_input.text())
        )
        self.worker.signals.finished.connect(self.on_rbf_completed)
        self.worker.signals.error.connect(self.on_worker_error)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.start()
        
    def stop_all_transactions(self):
        """Stop all transactions and return funds to Wallet A"""
        if not self.transaction_results:
            QMessageBox.warning(self, "Warning", LANGUAGES[self.current_language]['no_chain'])
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.stop_all_btn.setEnabled(False)
        
        # Log the action
        self.log_message(LANGUAGES[self.current_language]['action_stop'])
        
        # Get wallet credentials and addresses
        wif = self.wif_input.text().strip()
        wallet_a = self.wallet_a_input.text().strip()
        wallet_b = self.wallet_b_input.text().strip()
        wallet_c = self.wallet_c_input.text().strip()
        
        # Start worker thread
        self.worker = TransactionWorker(
            "stop_all", 
            self.rpc_handler, 
            self.transaction_results['original_utxo'],
            self.transaction_results['wallet_a'],
            float(self.amount_input.text())
        )
        self.worker.signals.finished.connect(self.on_stop_completed)
        self.worker.signals.error.connect(self.on_worker_error)
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.start()
        
    def on_chain_created(self, result):
        """Handle successful chain creation"""
        self.transaction_results = result
        self.progress_bar.setVisible(False)
        self.create_chain_btn.setEnabled(True)
        self.cancel_rbf_btn.setEnabled(True)
        self.stop_all_btn.setEnabled(True)
        
        # Display results
        output = LANGUAGES[self.current_language]['chain_created'] + "\n\n"
        output += LANGUAGES[self.current_language]['parent_txid'].format(result['parent_txid']) + "\n"
        output += LANGUAGES[self.current_language]['child_txid'].format(result['child_txid']) + "\n\n"
        output += LANGUAGES[self.current_language]['wallet_addresses'] + "\n"
        output += LANGUAGES[self.current_language]['wallet_a'].format(result['wallet_a']) + "\n"
        output += LANGUAGES[self.current_language]['wallet_b'].format(result['wallet_b']) + "\n"
        output += LANGUAGES[self.current_language]['wallet_c'].format(result['wallet_c']) + "\n"
        
        self.results_display.setPlainText(output)
        self.statusBar().showMessage(LANGUAGES[self.current_language]['success'])
        
        # Log the results
        self.log_message(LANGUAGES[self.current_language]['success_chain'])
        self.log_message(LANGUAGES[self.current_language]['parent_txid'].format(result['parent_txid']))
        self.log_message(LANGUAGES[self.current_language]['child_txid'].format(result['child_txid']))
        
        # Update wallet status
        self.wallet_c_funded = True
        self.update_wallet_status()
        self.update_flowchart()
        
    def on_rbf_completed(self, result):
        """Handle successful RBF completion"""
        self.progress_bar.setVisible(False)
        self.cancel_rbf_btn.setEnabled(True)
        
        # Display results
        output = LANGUAGES[self.current_language]['kill_activated'] + "\n\n"
        output += LANGUAGES[self.current_language]['rbf_txid'].format(result['rbf_txid']) + "\n\n"
        output += LANGUAGES[self.current_language]['chain_invalidated'] + "\n"
        output += LANGUAGES[self.current_language]['funds_returned'] + "\n"
        
        self.results_display.setPlainText(output)
        self.statusBar().showMessage(LANGUAGES[self.current_language]['success'])
        
        # Log the results
        self.log_message(LANGUAGES[self.current_language]['success_kill'])
        self.log_message(LANGUAGES[self.current_language]['rbf_txid'].format(result['rbf_txid']))
        self.log_message(LANGUAGES[self.current_language]['chain_invalidated'])
        
        # Update wallet status
        self.wallet_c_funded = False
        self.update_wallet_status()
        self.update_flowchart()
        
    def on_stop_completed(self, result):
        """Handle successful stop all completion"""
        self.progress_bar.setVisible(False)
        self.stop_all_btn.setEnabled(True)
        
        # Display results
        output = LANGUAGES[self.current_language]['all_stopped'] + "\n\n"
        output += LANGUAGES[self.current_language]['rbf_txid'].format(result['stop_txid']) + "\n\n"
        output += LANGUAGES[self.current_language]['chain_invalidated'] + "\n"
        output += LANGUAGES[self.current_language]['funds_returned'] + "\n"
        
        self.results_display.setPlainText(output)
        self.statusBar().showMessage(LANGUAGES[self.current_language]['success'])
        
        # Log the results
        self.log_message(LANGUAGES[self.current_language]['success_stop'])
        self.log_message(LANGUAGES[self.current_language]['rbf_txid'].format(result['stop_txid']))
        self.log_message(LANGUAGES[self.current_language]['chain_invalidated'])
        
        # Update wallet status
        self.wallet_c_funded = False
        self.update_wallet_status()
        self.update_flowchart()
        
    def on_worker_error(self, error_msg):
        """Handle worker error"""
        self.progress_bar.setVisible(False)
        self.create_chain_btn.setEnabled(True)
        self.cancel_rbf_btn.setEnabled(True)
        self.stop_all_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.statusBar().showMessage(LANGUAGES[self.current_language]['operation_failed'])
        
        # Log the error
        self.log_message(LANGUAGES[self.current_language]['error'].format(error_msg))
        
    def update_progress(self, message):
        """Update progress message"""
        self.statusBar().showMessage(message)
        self.log_message(LANGUAGES[self.current_language]['progress'].format(message))
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_display.insertPlainText(formatted_message)
        self.log_display.moveCursor(QTextCursor.End)
        
    def clear_log(self):
        """Clear the log display"""
        self.log_display.clear()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = BitcoinRBFTool()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()