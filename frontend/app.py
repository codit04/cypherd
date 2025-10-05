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
    st.write(f"**Address**: `{first_account.get('address', 'N/A')}`")
    st.write(f"**Balance**: {first_account.get('balance', '0.00')} ETH")
    
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
                        
                        st.success(f"Account created successfully! Address: {result.get('address', 'N/A')}")
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
        st.title("💸 Send Transaction")
        st.info("Send transaction page will be implemented in a future task.")
    elif page == "transactions":
        st.title("📜 Transaction History")
        st.info("Transaction history page will be implemented in a future task.")
    elif page == "settings":
        st.title("⚙️ Settings")
        st.info("Settings page will be implemented in a future task.")
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
