"""
Mock Web3 Wallet - Streamlit Frontend Application

Main entry point for the Streamlit web interface.
"""

import streamlit as st
from api_client import WalletAPIClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Mock Web3 Wallet",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
API_BASE_URL = os.getenv("API_BASE_URL") or os.getenv("BACKEND_API_URL", "http://localhost:8000")
api_client = WalletAPIClient(API_BASE_URL)


# ============================================================================
# Session State Initialization
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    import time
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "wallet_id" not in st.session_state:
        st.session_state.wallet_id = None
    
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
    
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    
    if "mnemonic_confirmed" not in st.session_state:
        st.session_state.mnemonic_confirmed = False


# ============================================================================
# Welcome/Authentication Page
# ============================================================================

def show_welcome_page():
    """Display the welcome/authentication page."""
    st.title("💰 Mock Web3 Wallet")
    st.markdown("---")
    
    # Check if user has an existing wallet
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🆕 Create New Wallet")
        st.write("Generate a new wallet with a secure 12-word mnemonic phrase.")
        
        if st.button("Create Wallet", key="create_wallet_btn", use_container_width=True):
            st.session_state.page = "create_wallet"
            st.rerun()
    
    with col2:
        st.subheader("📥 Import Existing Wallet")
        st.write("Restore your wallet using your 12-word mnemonic phrase.")
        
        if st.button("Import Wallet", key="import_wallet_btn", use_container_width=True):
            st.session_state.page = "import_wallet"
            st.rerun()
    
    st.markdown("---")
    
    # Unlock existing wallet section
    st.subheader("🔓 Unlock Wallet")
    st.write("If you already have a wallet, enter your wallet ID and password to unlock it.")
    
    with st.form("unlock_form"):
        wallet_id = st.text_input("Wallet ID", placeholder="Enter your wallet ID")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Unlock Wallet", use_container_width=True)
        
        if submit:
            if not wallet_id or not password:
                st.error("Please enter both wallet ID and password")
            else:
                unlock_wallet(wallet_id, password)


def show_create_wallet_page():
    """Display the create wallet page."""
    st.title("🆕 Create New Wallet")
    
    if st.button("← Back to Welcome", key="back_from_create"):
        st.session_state.page = "welcome"
        st.rerun()
    
    st.markdown("---")
    
    st.write("Create a new wallet by setting a secure password. You'll receive a 12-word mnemonic phrase that you must save securely.")
    
    st.warning("⚠️ **Important**: Your mnemonic phrase is the only way to recover your wallet. Write it down and store it in a safe place!")
    
    with st.form("create_wallet_form"):
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter a strong password (min 8 characters)",
            help="Choose a strong password with at least 8 characters"
        )
        password_confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password"
        )
        submit = st.form_submit_button("Create Wallet", use_container_width=True)
        
        if submit:
            if not password or not password_confirm:
                st.error("Please fill in all fields")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long")
            elif password != password_confirm:
                st.error("Passwords do not match")
            else:
                create_wallet(password)


def show_import_wallet_page():
    """Display the import wallet page."""
    st.title("📥 Import Wallet")
    
    if st.button("← Back to Welcome", key="back_from_import"):
        st.session_state.page = "welcome"
        st.rerun()
    
    st.markdown("---")
    
    st.write("Restore your wallet by entering your 12-word mnemonic phrase and setting a password.")
    
    with st.form("import_wallet_form"):
        mnemonic = st.text_area(
            "Mnemonic Phrase",
            placeholder="Enter your 12-word mnemonic phrase (separated by spaces)",
            help="Enter the 12 words from your mnemonic phrase, separated by spaces"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter a password (min 8 characters)",
            help="Set a password to protect your wallet"
        )
        password_confirm = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password"
        )
        submit = st.form_submit_button("Import Wallet", use_container_width=True)
        
        if submit:
            if not mnemonic or not password or not password_confirm:
                st.error("Please fill in all fields")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long")
            elif password != password_confirm:
                st.error("Passwords do not match")
            else:
                # Clean up mnemonic (remove extra spaces)
                mnemonic_clean = " ".join(mnemonic.strip().split())
                import_wallet(mnemonic_clean, password)


def show_mnemonic_confirmation(wallet_id, mnemonic, first_account):
    """Display mnemonic confirmation page after wallet creation."""
    st.title("✅ Wallet Created Successfully!")
    st.markdown("---")
    
    st.success(f"**Wallet ID**: `{wallet_id}`")
    
    st.warning("⚠️ **IMPORTANT: Save Your Mnemonic Phrase**")
    st.write("Write down these 12 words in order and store them in a safe place. You'll need them to recover your wallet.")
    
    # Display mnemonic in a nice format
    st.code(mnemonic, language=None)
    
    # Copy button
    if st.button("📋 Copy Mnemonic to Clipboard", use_container_width=True):
        st.write("Mnemonic copied! (Note: In a real app, this would copy to clipboard)")
        st.info(f"Mnemonic: {mnemonic}")
    
    st.markdown("---")
    
    # Show first account info
    st.subheader("Your First Account")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Address**: `{first_account.get('address', 'N/A')}`")
        st.write(f"**Balance**: {first_account.get('balance', '0.00')} ETH")
    
    with col2:
        st.write(f"**Label**: {first_account.get('label', 'Account 1')}")
        st.write(f"**Index**: {first_account.get('account_index', 0)}")
    
    # Show private key
    st.markdown("---")
    st.warning("⚠️ **Save Your Private Key**: You'll need this to sign transactions!")
    st.write("**🔐 Private Key:**")
    st.code(first_account.get('private_key', 'N/A'), language=None)
    
    if st.button("📋 Copy Private Key", key="copy_first_account_pk"):
        st.info(f"Private Key: {first_account.get('private_key', 'N/A')}")
    
    st.markdown("---")
    
    # Confirmation checkbox
    confirmed = st.checkbox(
        "✅ I have written down my mnemonic phrase and stored it securely",
        key="mnemonic_confirmation_checkbox"
    )
    
    if confirmed:
        if st.button("Continue to Wallet", use_container_width=True, type="primary"):
            # Authenticate the wallet
            st.session_state.authenticated = True
            st.session_state.wallet_id = wallet_id
            st.session_state.mnemonic_confirmed = True
            st.session_state.page = "dashboard"
            st.success("Welcome to your wallet!")
            st.rerun()
    else:
        st.info("Please confirm that you have saved your mnemonic phrase before continuing.")


# ============================================================================
# API Integration Functions
# ============================================================================

def create_wallet(password: str):
    """Create a new wallet via API."""
    try:
        with st.spinner("Creating wallet..."):
            result = api_client.create_wallet(password)
        
        if result:
            wallet_id = result.get("wallet_id")
            mnemonic = result.get("mnemonic")
            first_account = result.get("first_account", {})
            
            # Store in session state for confirmation page
            st.session_state.temp_wallet_id = wallet_id
            st.session_state.temp_mnemonic = mnemonic
            st.session_state.temp_first_account = first_account
            st.session_state.page = "mnemonic_confirmation"
            st.rerun()
    
    except Exception as e:
        st.error(f"Failed to create wallet: {str(e)}")


def import_wallet(mnemonic: str, password: str):
    """Import/restore a wallet via API."""
    try:
        with st.spinner("Importing wallet..."):
            result = api_client.restore_wallet(mnemonic, password)
        
        if result:
            wallet_id = result.get("wallet_id")
            exists = result.get("exists", False)
            accounts = result.get("accounts", [])
            
            st.session_state.authenticated = True
            st.session_state.wallet_id = wallet_id
            st.session_state.page = "dashboard"
            
            if exists:
                st.success(f"Wallet restored successfully! Found {len(accounts)} account(s).")
            else:
                st.success("Wallet imported successfully!")
            
            st.rerun()
    
    except Exception as e:
        st.error(f"Failed to import wallet: {str(e)}")


def unlock_wallet(wallet_id: str, password: str):
    """Unlock an existing wallet via API."""
    try:
        with st.spinner("Unlocking wallet..."):
            result = api_client.authenticate(wallet_id, password)
        
        if result and result.get("success"):
            st.session_state.authenticated = True
            st.session_state.wallet_id = wallet_id
            st.session_state.page = "dashboard"
            st.success("Wallet unlocked successfully!")
            st.rerun()
        else:
            st.error("Invalid wallet ID or password")
    
    except Exception as e:
        st.error(f"Failed to unlock wallet: {str(e)}")


# ============================================================================
# Dashboard and Authenticated Pages
# ============================================================================

def check_auto_lock():
    """Check if wallet should be auto-locked due to inactivity."""
    import time
    
    # Auto-lock timeout in seconds (15 minutes)
    AUTO_LOCK_TIMEOUT = 15 * 60
    
    if st.session_state.last_activity:
        elapsed = time.time() - st.session_state.last_activity
        if elapsed > AUTO_LOCK_TIMEOUT:
            # Auto-lock the wallet
            st.session_state.authenticated = False
            st.session_state.wallet_id = None
            st.session_state.page = "welcome"
            st.warning("Wallet locked due to inactivity")
            st.rerun()
    
    # Update last activity
    st.session_state.last_activity = time.time()


def show_dashboard():
    """Display the main dashboard page."""
    import time
    
    # Check auto-lock
    check_auto_lock()
    
    st.title("🏠 Dashboard")
    st.markdown("---")
    
    wallet_id = st.session_state.wallet_id
    
    # Display total wallet balance
    try:
        with st.spinner("Loading wallet balance..."):
            balance_data = api_client.get_total_balance(wallet_id)
        
        total_balance = float(balance_data.get("total_balance", 0))
        account_count = balance_data.get("account_count", 0)
        
        # Display balance in a prominent card
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.metric(
                label="💰 Total Wallet Balance",
                value=f"{total_balance:.8f} ETH",
                help="Combined balance across all accounts"
            )
        
        with col2:
            st.metric(
                label="📊 Accounts",
                value=account_count,
                help="Number of accounts in this wallet"
            )
        
        with col3:
            # Quick actions
            st.write("")  # Spacing
            if st.button("➕ Create Account", use_container_width=True):
                st.session_state.page = "accounts"
                st.rerun()
    
    except Exception as e:
        st.error(f"Failed to load wallet balance: {str(e)}")
    
    st.markdown("---")
    
    # Display accounts list
    st.subheader("📋 Your Accounts")
    
    try:
        with st.spinner("Loading accounts..."):
            accounts = api_client.get_accounts(wallet_id)
        
        if accounts:
            # Create a table-like display
            for account in accounts:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                    
                    with col1:
                        label = account.get("label") or f"Account {account.get('account_index', 0) + 1}"
                        st.write(f"**{label}**")
                    
                    with col2:
                        address = account.get("address", "")
                        # Truncate address for display
                        short_address = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address
                        st.code(short_address, language=None)
                    
                    with col3:
                        balance = float(account.get("balance", 0))
                        st.write(f"{balance:.8f} ETH")
                    
                    with col4:
                        if st.button("📋", key=f"copy_{account.get('id')}", help="Copy address"):
                            st.info(f"Address: {address}")
                    
                    st.markdown("---")
        else:
            st.info("No accounts found. Create your first account!")
    
    except Exception as e:
        st.error(f"Failed to load accounts: {str(e)}")
    
    # Quick action: Send Transaction
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💸 Send Transaction", use_container_width=True, type="primary"):
            st.session_state.page = "send"
            st.rerun()
    
    with col2:
        if st.button("📜 View All Transactions", use_container_width=True):
            st.session_state.page = "transactions"
            st.rerun()
    
    # Display recent transactions
    st.markdown("---")
    st.subheader("📊 Recent Transactions")
    
    try:
        # Get transactions from all accounts (limit to 5 most recent)
        all_transactions = []
        
        with st.spinner("Loading recent transactions..."):
            accounts = api_client.get_accounts(wallet_id)
            
            for account in accounts:
                try:
                    txs = api_client.get_account_transactions(account.get("id"), limit=5)
                    all_transactions.extend(txs)
                except Exception:
                    pass  # Skip accounts with no transactions
        
        # Sort by created_at (most recent first) and take top 5
        if all_transactions:
            all_transactions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            recent_transactions = all_transactions[:5]
            
            for tx in recent_transactions:
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                    
                    with col1:
                        tx_type = tx.get("transaction_type", "unknown")
                        if tx_type == "send":
                            st.write("📤 Send")
                        elif tx_type == "receive":
                            st.write("📥 Receive")
                        else:
                            st.write("🔄 Internal")
                    
                    with col2:
                        from_addr = tx.get("from_address", "")
                        to_addr = tx.get("to_address", "")
                        short_from = f"{from_addr[:6]}...{from_addr[-4:]}" if len(from_addr) > 10 else from_addr
                        short_to = f"{to_addr[:6]}...{to_addr[-4:]}" if len(to_addr) > 10 else to_addr
                        st.write(f"{short_from} → {short_to}")
                    
                    with col3:
                        amount = float(tx.get("amount", 0))
                        st.write(f"{amount:.8f} ETH")
                    
                    with col4:
                        status = tx.get("status", "unknown")
                        if status == "completed":
                            st.write("✅")
                        elif status == "pending":
                            st.write("⏳")
                        else:
                            st.write("❌")
                    
                    # Show memo if exists
                    memo = tx.get("memo")
                    if memo:
                        st.caption(f"💬 {memo}")
                    
                    st.markdown("---")
        else:
            st.info("No transactions yet. Send your first transaction!")
    
    except Exception as e:
        st.error(f"Failed to load recent transactions: {str(e)}")


def show_accounts_page():
    """Display the accounts management page."""
    check_auto_lock()
    
    st.title("👤 Accounts")
    st.markdown("---")
    
    wallet_id = st.session_state.wallet_id
    
    # Create Account button at the top
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Your Accounts")
    
    with col2:
        if st.button("➕ Create Account", use_container_width=True, type="primary"):
            st.session_state.show_create_account_form = True
            st.rerun()
    
    # Show new account details if just created
    if st.session_state.get("new_account_result"):
        result = st.session_state.new_account_result
        
        st.success("✅ Account Created Successfully!")
        
        with st.container():
            st.subheader("🔑 Account Details")
            st.warning("⚠️ **IMPORTANT**: Save your private key securely! You'll need it to sign transactions.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Address:**")
                st.code(result.get('address', 'N/A'), language=None)
                
                st.write("**Label:**")
                st.write(result.get('label', 'N/A'))
            
            with col2:
                st.write("**Balance:**")
                st.write(f"{result.get('balance', '0.0')} ETH")
                
                st.write("**Account Index:**")
                st.write(result.get('account_index', 0))
            
            st.markdown("---")
            
            st.write("**🔐 Private Key:**")
            st.code(result.get('private_key', 'N/A'), language=None)
            
            if st.button("📋 Copy Private Key", use_container_width=True):
                st.info(f"Private Key: {result.get('private_key', 'N/A')}")
            
            st.markdown("---")
            
            st.info("💡 **Tip**: Copy and save this private key. You'll need it to sign transactions in the Send page.")
            
            if st.button("✅ Got it, Continue", use_container_width=True, type="primary"):
                st.session_state.new_account_result = None
                st.rerun()
        
        st.markdown("---")
    
    # Show create account form if requested
    if st.session_state.get("show_create_account_form", False):
        with st.form("create_account_form"):
            st.subheader("Create New Account")
            label = st.text_input(
                "Account Label (optional)",
                placeholder="e.g., Savings, Trading, etc.",
                help="Give your account a memorable name"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your wallet password",
                help="Required to create a new account"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Create Account", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.show_create_account_form = False
                st.rerun()
            
            if submit:
                if not password:
                    st.error("Password is required")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            result = api_client.create_account(
                                wallet_id=wallet_id,
                                password=password,
                                label=label if label else None
                            )
                        
                        # Store the result in session state to display private key
                        st.session_state.new_account_result = result
                        st.session_state.show_create_account_form = False
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Failed to create account: {str(e)}")
        
        st.markdown("---")
    
    # Load and display accounts
    try:
        with st.spinner("Loading accounts..."):
            accounts = api_client.get_accounts(wallet_id)
        
        if not accounts:
            st.info("No accounts found. Create your first account using the button above!")
            return
        
        # Display accounts in a table-like format
        for idx, account in enumerate(accounts):
            account_id = account.get("id")
            address = account.get("address", "")
            label = account.get("label") or f"Account {account.get('account_index', 0) + 1}"
            balance = float(account.get("balance", 0))
            
            # Create expandable section for each account
            with st.expander(f"**{label}** - {balance:.8f} ETH", expanded=(idx == 0)):
                # Account details
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write("**Address:**")
                    st.code(address, language=None)
                
                with col2:
                    if st.button("📋 Copy", key=f"copy_addr_{account_id}", use_container_width=True):
                        st.info(f"Address copied: {address}")
                
                # Balance display
                st.metric(label="Balance", value=f"{balance:.8f} ETH")
                
                # Label editing
                st.markdown("---")
                st.write("**Edit Label:**")
                
                # Use a unique key for each account's label editor
                edit_key = f"edit_label_{account_id}"
                
                if st.session_state.get(edit_key, False):
                    # Show edit form
                    with st.form(f"edit_label_form_{account_id}"):
                        new_label = st.text_input(
                            "New Label",
                            value=account.get("label", ""),
                            placeholder="Enter new label"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            save = st.form_submit_button("💾 Save", use_container_width=True)
                        with col2:
                            cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                        
                        if save:
                            if new_label:
                                try:
                                    with st.spinner("Updating label..."):
                                        api_client.update_account_label(account_id, new_label)
                                    st.success("Label updated successfully!")
                                    st.session_state[edit_key] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to update label: {str(e)}")
                            else:
                                st.error("Label cannot be empty")
                        
                        if cancel_edit:
                            st.session_state[edit_key] = False
                            st.rerun()
                else:
                    # Show edit button
                    if st.button("✏️ Edit Label", key=f"edit_btn_{account_id}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                
                # Account-specific transaction history
                st.markdown("---")
                st.write("**Recent Transactions:**")
                
                try:
                    with st.spinner("Loading transactions..."):
                        transactions = api_client.get_account_transactions(account_id, limit=10)
                    
                    if transactions:
                        for tx in transactions:
                            tx_type = tx.get("transaction_type", "unknown")
                            from_addr = tx.get("from_address", "")
                            to_addr = tx.get("to_address", "")
                            amount = float(tx.get("amount", 0))
                            status = tx.get("status", "unknown")
                            memo = tx.get("memo")
                            created_at = tx.get("created_at", "")
                            
                            # Format addresses
                            short_from = f"{from_addr[:6]}...{from_addr[-4:]}" if len(from_addr) > 10 else from_addr
                            short_to = f"{to_addr[:6]}...{to_addr[-4:]}" if len(to_addr) > 10 else to_addr
                            
                            # Transaction card
                            with st.container():
                                col1, col2, col3 = st.columns([1, 2, 1])
                                
                                with col1:
                                    if tx_type == "send":
                                        st.write("📤 Send")
                                    elif tx_type == "receive":
                                        st.write("📥 Receive")
                                    else:
                                        st.write("🔄 Internal")
                                
                                with col2:
                                    st.write(f"{short_from} → {short_to}")
                                    if memo:
                                        st.caption(f"💬 {memo}")
                                
                                with col3:
                                    st.write(f"{amount:.8f} ETH")
                                    if status == "completed":
                                        st.caption("✅ Completed")
                                    elif status == "pending":
                                        st.caption("⏳ Pending")
                                    else:
                                        st.caption("❌ Failed")
                                
                                st.caption(f"🕒 {created_at}")
                                st.markdown("---")
                    else:
                        st.info("No transactions yet for this account.")
                
                except Exception as e:
                    st.error(f"Failed to load transactions: {str(e)}")
    
    except Exception as e:
        st.error(f"Failed to load accounts: {str(e)}")


def show_send_transaction_page():
    """Display the send transaction page with signature approval flow."""
    check_auto_lock()
    
    st.title("💸 Send Transaction")
    st.markdown("---")
    
    wallet_id = st.session_state.wallet_id
    
    # Load accounts for the from account dropdown
    try:
        with st.spinner("Loading accounts..."):
            accounts = api_client.get_accounts(wallet_id)
        
        if not accounts:
            st.warning("No accounts found. Please create an account first.")
            if st.button("← Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
            return
        
        # Initialize session state for transaction flow
        if "tx_approval_data" not in st.session_state:
            st.session_state.tx_approval_data = None
        if "tx_approval_expires_at" not in st.session_state:
            st.session_state.tx_approval_expires_at = None
        if "tx_message_id" not in st.session_state:
            st.session_state.tx_message_id = None
        if "tx_from_account" not in st.session_state:
            st.session_state.tx_from_account = None
        
        # Check if we're in approval/confirmation mode
        if st.session_state.tx_approval_data:
            show_transaction_approval()
        else:
            show_transaction_form(accounts)
    
    except Exception as e:
        st.error(f"Failed to load accounts: {str(e)}")


def show_transaction_form(accounts):
    """Display the transaction form."""
    st.subheader("Transaction Details")
    
    with st.form("send_transaction_form"):
        # From account dropdown
        account_options = {}
        for account in accounts:
            label = account.get("label") or f"Account {account.get('account_index', 0) + 1}"
            address = account.get("address", "")
            balance = float(account.get("balance", 0))
            short_address = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address
            display_text = f"{label} ({short_address}) - {balance:.8f} ETH"
            account_options[display_text] = account
        
        selected_account_display = st.selectbox(
            "From Account",
            options=list(account_options.keys()),
            help="Select the account to send from"
        )
        selected_account = account_options[selected_account_display]
        
        # To address input
        to_address = st.text_input(
            "To Address",
            placeholder="0x...",
            help="Enter the recipient's Ethereum address"
        )
        
        # Amount input with ETH/USD toggle
        col1, col2 = st.columns([3, 1])
        
        with col1:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.8f",
                help="Enter the amount to send"
            )
        
        with col2:
            currency = st.selectbox(
                "Currency",
                options=["ETH", "USD"],
                help="Select currency for amount"
            )
        
        # Memo input
        memo = st.text_area(
            "Memo (optional)",
            placeholder="Add a note for this transaction",
            max_chars=200,
            help="Optional message to include with the transaction"
        )
        
        # Display current balance
        current_balance = float(selected_account.get("balance", 0))
        st.info(f"💰 Available Balance: {current_balance:.8f} ETH")
        
        # Submit button
        submit = st.form_submit_button("Create Approval", use_container_width=True, type="primary")
        
        if submit:
            # Validation
            if not to_address:
                st.error("Please enter a recipient address")
            elif not to_address.startswith("0x") or len(to_address) != 42:
                st.error("Invalid Ethereum address format. Address must start with 0x and be 42 characters long.")
            elif amount <= 0:
                st.error("Amount must be greater than 0")
            elif currency == "ETH" and amount > current_balance:
                st.error(f"Insufficient balance. You have {current_balance:.8f} ETH available.")
            else:
                # Create approval
                create_transaction_approval(
                    selected_account.get("id"),
                    selected_account.get("address"),
                    to_address,
                    amount,
                    currency,
                    memo if memo else None
                )


def create_transaction_approval(from_account_id, from_address, to_address, amount, currency, memo):
    """Create transaction approval via API."""
    try:
        with st.spinner("Creating approval message..."):
            # Prepare request based on currency
            if currency == "ETH":
                result = api_client.create_approval(
                    from_account_id=from_account_id,
                    to_address=to_address,
                    amount_eth=amount,
                    amount_usd=None,
                    memo=memo
                )
            else:  # USD
                result = api_client.create_approval(
                    from_account_id=from_account_id,
                    to_address=to_address,
                    amount_eth=None,
                    amount_usd=amount,
                    memo=memo
                )
        
        # Store approval data in session state
        st.session_state.tx_approval_data = result
        st.session_state.tx_message_id = result.get("message_id")
        st.session_state.tx_approval_expires_at = result.get("expires_at")
        st.session_state.tx_from_account = from_address
        
        st.success("Approval message created! Please review and confirm the transaction.")
        st.rerun()
    
    except Exception as e:
        st.error(f"Failed to create approval: {str(e)}")


def show_transaction_approval():
    """Display the transaction approval with countdown and signature confirmation."""
    import time
    from datetime import datetime
    from eth_account import Account
    from eth_account.messages import encode_defunct
    
    approval_data = st.session_state.tx_approval_data
    message = approval_data.get("message")
    message_id = approval_data.get("message_id")
    expires_at_str = approval_data.get("expires_at")
    eth_amount = float(approval_data.get("eth_amount", 0))
    usd_amount = approval_data.get("usd_amount")
    from_address = st.session_state.tx_from_account
    
    st.subheader("⚠️ Transaction Approval Required")
    st.markdown("---")
    
    # Display approval message
    st.write("**Approval Message:**")
    st.code(message, language=None)
    
    # Display transaction details
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Amount (ETH)", value=f"{eth_amount:.8f} ETH")
    
    with col2:
        if usd_amount:
            st.metric(label="Amount (USD)", value=f"${float(usd_amount):.2f}")
    
    st.markdown("---")
    
    # Parse expiration time and calculate remaining time
    try:
        # Parse ISO format datetime
        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
        now = datetime.now(expires_at.tzinfo)
        remaining_seconds = (expires_at - now).total_seconds()
        
        if remaining_seconds <= 0:
            st.error("⏰ Approval message has expired. Please create a new transaction.")
            if st.button("Start Over", use_container_width=True):
                clear_transaction_state()
                st.rerun()
            return
        
        # Display countdown timer
        st.warning(f"⏱️ Time remaining: {int(remaining_seconds)} seconds")
        
        # Progress bar
        progress = remaining_seconds / 30.0  # 30 seconds total
        st.progress(progress)
        
    except Exception as e:
        st.error(f"Error parsing expiration time: {str(e)}")
        remaining_seconds = 0
    
    st.markdown("---")
    
    # Signature section
    st.subheader("🔐 Sign Transaction")
    st.write("To confirm this transaction, you need to sign the approval message with your account's private key.")
    
    with st.form("signature_form"):
        st.warning("⚠️ **Security Note**: In a production environment, signing would happen in a secure wallet extension. For this mock wallet, you need to provide the private key.")
        
        private_key = st.text_input(
            "Private Key",
            type="password",
            placeholder="Enter your account's private key (0x...)",
            help="The private key for the sending account"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            confirm = st.form_submit_button("✅ Confirm & Sign", use_container_width=True, type="primary")
        
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            clear_transaction_state()
            st.success("Transaction cancelled.")
            st.rerun()
        
        if confirm:
            if not private_key:
                st.error("Please enter your private key to sign the transaction")
            else:
                # Sign the message
                try:
                    # Ensure private key has 0x prefix
                    if not private_key.startswith("0x"):
                        private_key = "0x" + private_key
                    
                    # Create account from private key
                    account = Account.from_key(private_key)
                    
                    # Verify the account address matches the from address
                    if account.address.lower() != from_address.lower():
                        st.error(f"Private key does not match the sending account address. Expected: {from_address}, Got: {account.address}")
                    else:
                        # Sign the message using Ethereum's personal_sign standard
                        message_hash = encode_defunct(text=message)
                        signed_message = account.sign_message(message_hash)
                        signature = signed_message.signature.hex()
                        
                        # Send the signed transaction
                        send_signed_transaction(message_id, signature)
                
                except ValueError as e:
                    st.error(f"Invalid private key format: {str(e)}")
                except Exception as e:
                    st.error(f"Failed to sign message: {str(e)}")
    
    # Auto-refresh to update countdown
    if remaining_seconds > 0:
        time.sleep(1)
        st.rerun()


def send_signed_transaction(message_id, signature):
    """Send the signed transaction to the backend."""
    try:
        with st.spinner("Sending transaction..."):
            result = api_client.send_transaction(message_id, signature)
        
        # Clear transaction state
        clear_transaction_state()
        
        # Display success
        st.success("✅ Transaction sent successfully!")
        
        # Display transaction details
        st.subheader("Transaction Details")
        
        tx_id = result.get("transaction_id")
        from_addr = result.get("from_address")
        to_addr = result.get("to_address")
        amount = float(result.get("amount", 0))
        memo = result.get("memo")
        status = result.get("status")
        created_at = result.get("created_at")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Transaction ID:** `{tx_id}`")
            st.write(f"**From:** `{from_addr}`")
            st.write(f"**To:** `{to_addr}`")
        
        with col2:
            st.write(f"**Amount:** {amount:.8f} ETH")
            st.write(f"**Status:** {status}")
            if memo:
                st.write(f"**Memo:** {memo}")
        
        st.write(f"**Timestamp:** {created_at}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Send Another Transaction", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("Back to Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
    
    except Exception as e:
        error_message = str(e)
        
        # Handle specific error cases
        if "insufficient balance" in error_message.lower():
            st.error("❌ Transaction failed: Insufficient balance")
        elif "invalid address" in error_message.lower():
            st.error("❌ Transaction failed: Invalid recipient address")
        elif "expired" in error_message.lower():
            st.error("❌ Transaction failed: Approval message has expired. Please create a new transaction.")
        elif "price tolerance" in error_message.lower():
            st.error("❌ Transaction failed: Price has changed by more than 1% since approval. Please create a new transaction.")
        elif "signature" in error_message.lower():
            st.error("❌ Transaction failed: Invalid signature. Please ensure you're using the correct private key.")
        else:
            st.error(f"❌ Transaction failed: {error_message}")
        
        # Clear transaction state on error
        clear_transaction_state()
        
        if st.button("Try Again", use_container_width=True):
            st.rerun()


def clear_transaction_state():
    """Clear transaction-related session state."""
    st.session_state.tx_approval_data = None
    st.session_state.tx_approval_expires_at = None
    st.session_state.tx_message_id = None
    st.session_state.tx_from_account = None


def show_transaction_history_page():
    """Display the transaction history page with filtering options."""
    check_auto_lock()
    
    st.title("📜 Transaction History")
    st.markdown("---")
    
    wallet_id = st.session_state.wallet_id
    
    # Load accounts for filter dropdown
    try:
        with st.spinner("Loading accounts..."):
            accounts = api_client.get_accounts(wallet_id)
        
        if not accounts:
            st.warning("No accounts found. Please create an account first.")
            if st.button("← Back to Dashboard"):
                st.session_state.page = "dashboard"
                st.rerun()
            return
        
        # Account filter dropdown
        st.subheader("🔍 Filter Transactions")
        
        # Create filter options
        filter_options = ["All Accounts"]
        for acc in accounts:
            label = acc.get('label') or f"Account {acc.get('account_index', 0) + 1}"
            address = acc.get('address', '')
            short_addr = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address
            filter_options.append(f"{label} ({short_addr})")
        
        # Initialize filter state if not exists
        if "tx_filter_index" not in st.session_state:
            st.session_state.tx_filter_index = 0
        
        selected_filter = st.selectbox(
            "Select Account",
            options=filter_options,
            index=st.session_state.tx_filter_index,
            help="Filter transactions by account or view all"
        )
        
        # Update filter index
        st.session_state.tx_filter_index = filter_options.index(selected_filter)
        
        st.markdown("---")
        
        # Determine which account(s) to fetch transactions for
        selected_account_id = None
        if selected_filter != "All Accounts":
            # Extract account index from selection
            selected_index = filter_options.index(selected_filter) - 1
            selected_account_id = accounts[selected_index].get("id")
        
        # Fetch transactions
        all_transactions = []
        
        with st.spinner("Loading transactions..."):
            if selected_account_id:
                # Fetch transactions for specific account
                try:
                    transactions = api_client.get_account_transactions(selected_account_id, limit=100)
                    all_transactions.extend(transactions)
                except Exception as e:
                    st.error(f"Failed to load transactions: {str(e)}")
            else:
                # Fetch transactions for all accounts
                for account in accounts:
                    try:
                        transactions = api_client.get_account_transactions(account.get("id"), limit=100)
                        all_transactions.extend(transactions)
                    except Exception:
                        pass  # Skip accounts with errors
        
        # Sort transactions by timestamp (most recent first)
        if all_transactions:
            all_transactions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Display transaction count
        st.subheader(f"📊 Transactions ({len(all_transactions)})")
        
        if not all_transactions:
            # Empty state
            st.info("🔍 No transactions found.")
            st.write("Once you send or receive transactions, they will appear here.")
            
            if st.button("💸 Send Your First Transaction", use_container_width=True, type="primary"):
                st.session_state.page = "send"
                st.rerun()
        else:
            # Display transactions
            for idx, tx in enumerate(all_transactions):
                tx_id = tx.get("id", "")
                tx_type = tx.get("transaction_type", "unknown")
                from_addr = tx.get("from_address", "")
                to_addr = tx.get("to_address", "")
                amount = float(tx.get("amount", 0))
                memo = tx.get("memo")
                status = tx.get("status", "unknown")
                created_at = tx.get("created_at", "")
                
                # Format addresses
                short_from = f"{from_addr[:6]}...{from_addr[-4:]}" if len(from_addr) > 10 else from_addr
                short_to = f"{to_addr[:6]}...{to_addr[-4:]}" if len(to_addr) > 10 else to_addr
                short_tx_id = f"{tx_id[:8]}...{tx_id[-8:]}" if len(tx_id) > 16 else tx_id
                
                # Transaction card with expander
                with st.expander(
                    f"{'📤' if tx_type == 'send' else '📥' if tx_type == 'receive' else '🔄'} "
                    f"{amount:.8f} ETH - {short_from} → {short_to}",
                    expanded=(idx == 0)  # Expand first transaction by default
                ):
                    # Transaction details in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Transaction ID:**")
                        st.code(short_tx_id, language=None)
                        
                        if st.button("📋 Copy Full ID", key=f"copy_tx_{idx}", use_container_width=True):
                            st.info(f"Transaction ID: {tx_id}")
                        
                        st.write("**Type:**")
                        if tx_type == "send":
                            st.write("📤 Send")
                        elif tx_type == "receive":
                            st.write("📥 Receive")
                        elif tx_type == "internal":
                            st.write("🔄 Internal Transfer")
                        else:
                            st.write(f"❓ {tx_type}")
                        
                        st.write("**Status:**")
                        if status == "completed":
                            st.success("✅ Completed")
                        elif status == "pending":
                            st.warning("⏳ Pending")
                        elif status == "failed":
                            st.error("❌ Failed")
                        else:
                            st.write(f"❓ {status}")
                    
                    with col2:
                        st.write("**Amount:**")
                        st.metric(label="", value=f"{amount:.8f} ETH")
                        
                        st.write("**Timestamp:**")
                        st.write(f"🕒 {created_at}")
                    
                    st.markdown("---")
                    
                    # From and To addresses
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**From Address:**")
                        st.code(from_addr, language=None)
                        if st.button("📋 Copy", key=f"copy_from_{idx}", use_container_width=True):
                            st.info(f"From Address: {from_addr}")
                    
                    with col2:
                        st.write("**To Address:**")
                        st.code(to_addr, language=None)
                        if st.button("📋 Copy", key=f"copy_to_{idx}", use_container_width=True):
                            st.info(f"To Address: {to_addr}")
                    
                    # Memo if exists
                    if memo:
                        st.markdown("---")
                        st.write("**Memo:**")
                        st.info(f"💬 {memo}")
                
                # Separator between transactions
                if idx < len(all_transactions) - 1:
                    st.markdown("---")
        
        # Refresh button at the bottom
        st.markdown("---")
        if st.button("🔄 Refresh Transactions", use_container_width=True):
            st.rerun()
    
    except Exception as e:
        st.error(f"Failed to load transaction history: {str(e)}")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()


def show_settings_page():
    """Display the settings page."""
    check_auto_lock()
    
    st.title("⚙️ Settings")
    st.markdown("---")
    
    wallet_id = st.session_state.wallet_id
    
    # ========================================================================
    # Wallet Information Section
    # ========================================================================
    st.subheader("📊 Wallet Information")
    
    try:
        with st.spinner("Loading wallet information..."):
            wallet_info = api_client.get_wallet_info(wallet_id)
            accounts = api_client.get_accounts(wallet_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Wallet ID:**")
            st.code(wallet_id, language=None)
            
            created_at = wallet_info.get("created_at", "N/A")
            st.write(f"**Created:** {created_at}")
        
        with col2:
            num_accounts = len(accounts)
            st.metric(label="Number of Accounts", value=num_accounts)
            
            last_accessed = wallet_info.get("last_accessed", "N/A")
            st.write(f"**Last Accessed:** {last_accessed}")
    
    except Exception as e:
        st.error(f"Failed to load wallet information: {str(e)}")
    
    st.markdown("---")
    
    # ========================================================================
    # Change Password Section
    # ========================================================================
    st.subheader("🔐 Change Password")
    
    with st.form("change_password_form"):
        st.write("Update your wallet password. You'll need to enter your current password.")
        
        old_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password (min 8 characters)"
        )
        
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter new password"
        )
        
        submit_password = st.form_submit_button("Change Password", use_container_width=True)
        
        if submit_password:
            if not old_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields")
            elif len(new_password) < 8:
                st.error("New password must be at least 8 characters long")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif old_password == new_password:
                st.error("New password must be different from current password")
            else:
                try:
                    with st.spinner("Changing password..."):
                        result = api_client.change_password(
                            wallet_id=wallet_id,
                            old_password=old_password,
                            new_password=new_password
                        )
                    
                    st.success("✅ Password changed successfully!")
                    st.info("Please use your new password for future logins.")
                
                except Exception as e:
                    st.error(f"Failed to change password: {str(e)}")
    
    st.markdown("---")
    
    # ========================================================================
    # Lock Wallet Section
    # ========================================================================
    st.subheader("🔒 Lock Wallet")
    st.write("Lock your wallet to require password authentication for future access.")
    
    if st.button("🔒 Lock Wallet Now", use_container_width=True, type="secondary"):
        try:
            with st.spinner("Locking wallet..."):
                api_client.lock_wallet(wallet_id)
            
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.wallet_id = None
            st.session_state.page = "welcome"
            
            st.success("Wallet locked successfully!")
            st.rerun()
        
        except Exception as e:
            st.error(f"Failed to lock wallet: {str(e)}")
    
    st.markdown("---")
    
    # ========================================================================
    # Notification Preferences Section
    # ========================================================================
    st.subheader("📱 Notification Preferences")
    st.write("Configure WhatsApp notifications for transaction and security alerts.")
    
    # Load existing preferences
    try:
        with st.spinner("Loading notification preferences..."):
            try:
                prefs = api_client.get_notification_preferences(wallet_id)
                existing_prefs = True
            except Exception:
                # No preferences set yet, use defaults
                prefs = {
                    "phone_number": "",
                    "enabled": False,
                    "notify_incoming": True,
                    "notify_outgoing": True,
                    "notify_security": True
                }
                existing_prefs = False
        
        with st.form("notification_preferences_form"):
            # Phone number input
            phone_number = st.text_input(
                "Phone Number",
                value=prefs.get("phone_number", ""),
                placeholder="+1234567890",
                help="Enter phone number in international format: +[country_code][number]"
            )
            
            st.caption("📝 Format: +[country code][number] (e.g., +1234567890 for US, +919876543210 for India)")
            
            # Enable/disable toggle
            enabled = st.checkbox(
                "Enable Notifications",
                value=prefs.get("enabled", False),
                help="Turn on/off all WhatsApp notifications"
            )
            
            st.markdown("**Notification Types:**")
            
            # Notification type checkboxes
            col1, col2, col3 = st.columns(3)
            
            with col1:
                notify_incoming = st.checkbox(
                    "📥 Incoming Transactions",
                    value=prefs.get("notify_incoming", True),
                    help="Notify when you receive funds"
                )
            
            with col2:
                notify_outgoing = st.checkbox(
                    "📤 Outgoing Transactions",
                    value=prefs.get("notify_outgoing", True),
                    help="Notify when you send funds"
                )
            
            with col3:
                notify_security = st.checkbox(
                    "🔐 Security Alerts",
                    value=prefs.get("notify_security", True),
                    help="Notify on security events"
                )
            
            # Submit button
            col1, col2 = st.columns(2)
            
            with col1:
                submit_prefs = st.form_submit_button(
                    "💾 Save Preferences",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                test_notification = st.form_submit_button(
                    "📨 Test Notification",
                    use_container_width=True
                )
            
            if submit_prefs:
                # Validate phone number format if notifications are enabled
                if enabled and not phone_number:
                    st.error("Phone number is required when notifications are enabled")
                elif enabled and not phone_number.startswith("+"):
                    st.error("Phone number must start with + followed by country code")
                elif enabled and len(phone_number) < 10:
                    st.error("Phone number appears to be too short")
                else:
                    try:
                        with st.spinner("Saving notification preferences..."):
                            result = api_client.set_notification_preferences(
                                wallet_id=wallet_id,
                                phone_number=phone_number if phone_number else None,
                                enabled=enabled,
                                notify_incoming=notify_incoming,
                                notify_outgoing=notify_outgoing,
                                notify_security=notify_security
                            )
                        
                        st.success("✅ Notification preferences saved successfully!")
                        
                        if enabled:
                            st.info("💡 Notifications are now enabled. You'll receive WhatsApp messages for selected events.")
                        else:
                            st.info("Notifications are disabled. Enable them to receive WhatsApp alerts.")
                        
                        # Rerun to refresh the form with new values
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Failed to save notification preferences: {str(e)}")
            
            if test_notification:
                # Validate phone number before testing
                if not phone_number:
                    st.error("Please enter a phone number to test")
                elif not phone_number.startswith("+"):
                    st.error("Phone number must start with + followed by country code")
                elif len(phone_number) < 10:
                    st.error("Phone number appears to be too short")
                else:
                    try:
                        with st.spinner("Sending test notification..."):
                            result = api_client.test_notification(phone_number)
                        
                        if result.get("success"):
                            st.success("✅ Test notification sent! Check your WhatsApp.")
                            st.info("💡 If you didn't receive the message, verify your phone number format and WhatsApp Web access.")
                        else:
                            st.warning(f"⚠️ {result.get('message', 'Failed to send test notification')}")
                    
                    except Exception as e:
                        st.error(f"Failed to send test notification: {str(e)}")
                        st.info("💡 Make sure WhatsApp Web is accessible and the phone number is correct.")
    
    except Exception as e:
        st.error(f"Failed to load notification preferences: {str(e)}")
    
    st.markdown("---")
    
    # ========================================================================
    # Additional Information
    # ========================================================================
    st.subheader("ℹ️ About Notifications")
    
    with st.expander("How do WhatsApp notifications work?"):
        st.write("""
        **WhatsApp Notification System:**
        
        - Notifications are sent via WhatsApp Web using the pywhatkit library
        - You'll receive messages for:
          - **Incoming transactions**: When someone sends you funds
          - **Outgoing transactions**: When you send funds to another address
          - **Security alerts**: Password changes and other security events
        
        **Requirements:**
        - Valid phone number with WhatsApp account
        - WhatsApp Web must be accessible from the server
        - Phone number must be in international format: +[country_code][number]
        
        **Privacy:**
        - Your phone number is stored securely
        - Notifications can be disabled at any time
        - You control which types of notifications you receive
        
        **Note:** This is a mock implementation for demonstration purposes.
        In a production environment, you would use WhatsApp Business API or similar services.
        """)


def show_authenticated_app():
    """Show the authenticated application with navigation."""
    # Sidebar navigation
    with st.sidebar:
        st.title("💰 Mock Web3 Wallet")
        st.markdown("---")
        
        # Navigation menu
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("👤 Accounts", use_container_width=True):
            st.session_state.page = "accounts"
            st.rerun()
        
        if st.button("💸 Send", use_container_width=True):
            st.session_state.page = "send"
            st.rerun()
        
        if st.button("📜 Transactions", use_container_width=True):
            st.session_state.page = "transactions"
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()
        
        st.markdown("---")
        
        # Wallet info
        st.caption(f"**Wallet ID:**")
        wallet_id = st.session_state.wallet_id
        short_wallet_id = f"{wallet_id[:8]}...{wallet_id[-8:]}" if len(wallet_id) > 16 else wallet_id
        st.caption(short_wallet_id)
        
        st.markdown("---")
        
        # Lock wallet button
        if st.button("🔒 Lock Wallet", use_container_width=True, type="secondary"):
            try:
                api_client.lock_wallet(st.session_state.wallet_id)
                st.session_state.authenticated = False
                st.session_state.wallet_id = None
                st.session_state.page = "welcome"
                st.success("Wallet locked successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to lock wallet: {str(e)}")
    
    # Main content area - route to appropriate page
    page = st.session_state.get("page", "dashboard")
    
    if page == "dashboard":
        show_dashboard()
    elif page == "accounts":
        show_accounts_page()
    elif page == "send":
        show_send_transaction_page()
    elif page == "transactions":
        show_transaction_history_page()
    elif page == "settings":
        show_settings_page()
    else:
        # Default to dashboard
        show_dashboard()


# ============================================================================
# Main Application Logic
# ============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Route to appropriate page based on session state
    if not st.session_state.authenticated:
        # Show welcome/authentication pages
        if st.session_state.page == "welcome":
            show_welcome_page()
        elif st.session_state.page == "create_wallet":
            show_create_wallet_page()
        elif st.session_state.page == "import_wallet":
            show_import_wallet_page()
        elif st.session_state.page == "mnemonic_confirmation":
            # Show mnemonic confirmation after wallet creation
            show_mnemonic_confirmation(
                st.session_state.temp_wallet_id,
                st.session_state.temp_mnemonic,
                st.session_state.temp_first_account
            )
    else:
        # User is authenticated - show main application with navigation
        show_authenticated_app()


if __name__ == "__main__":
    main()
