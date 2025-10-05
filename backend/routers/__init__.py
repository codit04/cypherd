"""
Routers package initialization.

Exports all API routers for the Mock Web3 Wallet application.
"""

from backend.routers import wallet, accounts, transactions, notifications

__all__ = ['wallet', 'accounts', 'transactions', 'notifications']
