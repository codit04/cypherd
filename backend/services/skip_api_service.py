"""
Skip API Service - Integration with Skip API for ETH/USD price conversion.

Handles querying Skip API for price quotes and decimal precision conversions.
"""

from typing import Dict, Any
from decimal import Decimal
from pathlib import Path
import json
import httpx
import logging

# Configure logging
logger = logging.getLogger(__name__)


class SkipAPIService:
    """Service for Skip API integration and price conversion."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Skip API Service.
        
        Args:
            config_path: Optional path to config file. If None, uses default location.
        """
        if config_path is None:
            # Default config path relative to this file
            config_path = Path(__file__).parent.parent / "config" / "skip_api_config.json"
        
        # Load configuration from JSON file
        self._load_config(config_path)
    
    def _load_config(self, config_path: Path) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Set configuration attributes
            self.SKIP_API_URL = config['api_url']
            self.USDC_CONTRACT = config['usdc_contract']
            self.ETH_DENOM = config['eth_denom']
            self.CHAIN_ID = config['chain_id']
            self.USDC_DECIMALS = config['usdc_decimals']
            self.ETH_DECIMALS = config['eth_decimals']
            self.API_TIMEOUT = config['api_timeout']
            self.RECIPIENT_ADDRESS = config['recipient_address']
            self.SLIPPAGE_TOLERANCE_PERCENT = config['slippage_tolerance_percent']
            self.DEFAULT_PRICE_TOLERANCE_PERCENT = Decimal(config['default_price_tolerance_percent'])
            
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Skip API config file not found: {config_path}")
        except KeyError as e:
            logger.error(f"Missing required config key: {e}")
            raise ValueError(f"Invalid config file - missing key: {e}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise ValueError(f"Failed to load Skip API config: {e}")
    
    def convert_usd_to_usdc_units(self, usd_amount: Decimal) -> int:
        """
        Convert USD amount to USDC units with 6 decimal precision.
        
        USDC uses 6 decimal places, so:
        - 1.0 USD = 1,000,000 units
        - 0.5 USD = 500,000 units
        - 100.25 USD = 100,250,000 units
        
        Args:
            usd_amount: USD amount as Decimal
            
        Returns:
            int: USDC units (6 decimal precision)
            
        Example:
            >>> convert_usd_to_usdc_units(Decimal("1.0"))
            1000000
            >>> convert_usd_to_usdc_units(Decimal("100.25"))
            100250000
        """
        # Multiply by 10^6 to convert to USDC units
        usdc_units = int(usd_amount * Decimal(10 ** self.USDC_DECIMALS))
        return usdc_units
    
    def convert_eth_units_to_eth(self, eth_units: int) -> Decimal:
        """
        Convert ETH units (wei) to ETH with 18 decimal precision.
        
        ETH uses 18 decimal places (wei), so:
        - 1,000,000,000,000,000,000 units = 1.0 ETH
        - 500,000,000,000,000,000 units = 0.5 ETH
        - 1,500,000,000,000,000 units = 0.0015 ETH
        
        Args:
            eth_units: ETH amount in wei (18 decimal precision)
            
        Returns:
            Decimal: ETH amount
            
        Example:
            >>> convert_eth_units_to_eth(1000000000000000000)
            Decimal('1.0')
            >>> convert_eth_units_to_eth(500000000000000000)
            Decimal('0.5')
        """
        # Divide by 10^18 to convert from wei to ETH
        eth_amount = Decimal(eth_units) / Decimal(10 ** self.ETH_DECIMALS)
        return eth_amount
    
    def get_eth_quote_for_usd(self, usd_amount: Decimal) -> Dict[str, Any]:
        """
        Query Skip API to get ETH equivalent for a USD amount.
        
        This method:
        1. Converts USD to USDC units (6 decimals)
        2. Queries Skip API with proper request body
        3. Parses response to extract ETH amount
        4. Converts ETH units to ETH (18 decimals)
        5. Returns structured quote data
        
        Args:
            usd_amount: USD amount to convert
            
        Returns:
            Dict containing:
                - eth_amount: ETH equivalent as Decimal
                - usd_amount: Original USD amount as Decimal
                - rate: Exchange rate (ETH per USD) as Decimal
                - raw_response: Raw API response for debugging
                
        Raises:
            ValueError: If USD amount is invalid
            TimeoutError: If API request times out
            Exception: If API request fails or response is invalid
            
        Example:
            >>> get_eth_quote_for_usd(Decimal("100.0"))
            {
                'eth_amount': Decimal('0.045'),
                'usd_amount': Decimal('100.0'),
                'rate': Decimal('0.00045'),
                'raw_response': {...}
            }
        """
        # Validate USD amount
        if usd_amount <= 0:
            raise ValueError("USD amount must be greater than 0")
        
        # Convert USD to USDC units
        usdc_units = self.convert_usd_to_usdc_units(usd_amount)
        
        # Build request body for Skip API
        request_body = {
            "source_asset_denom": self.USDC_CONTRACT,
            "source_asset_chain_id": self.CHAIN_ID,
            "dest_asset_denom": self.ETH_DENOM,
            "dest_asset_chain_id": self.CHAIN_ID,
            "amount_in": str(usdc_units),
            "chain_ids_to_addresses": {
                self.CHAIN_ID: self.RECIPIENT_ADDRESS
            },
            "slippage_tolerance_percent": self.SLIPPAGE_TOLERANCE_PERCENT,
            "smart_swap_options": {
                "evm_swaps": True
            },
            "allow_unsafe": False
        }
        
        try:
            # Make API request with timeout
            with httpx.Client(timeout=self.API_TIMEOUT) as client:
                response = client.post(
                    self.SKIP_API_URL,
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                
                # Check for HTTP errors
                response.raise_for_status()
                
                # Parse JSON response
                response_data = response.json()
                
        except httpx.TimeoutException as e:
            logger.error(f"Skip API request timed out: {e}")
            raise TimeoutError(f"Skip API request timed out after {self.API_TIMEOUT} seconds")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Skip API returned error status: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Skip API request failed with status {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"Skip API request failed: {e}")
            raise Exception(f"Skip API request failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error querying Skip API: {e}")
            raise Exception(f"Failed to query Skip API: {str(e)}")
        
        # Parse ETH amount from response
        try:
            eth_amount = self._parse_eth_amount_from_response(response_data)
        except Exception as e:
            logger.error(f"Failed to parse Skip API response: {e}")
            raise Exception(f"Failed to parse Skip API response: {str(e)}")
        
        # Calculate exchange rate
        rate = eth_amount / usd_amount if usd_amount > 0 else Decimal('0')
        
        return {
            'eth_amount': eth_amount,
            'usd_amount': usd_amount,
            'rate': rate,
            'raw_response': response_data
        }
    
    def check_price_tolerance(
        self,
        original_quote: Decimal,
        new_quote: Decimal,
        tolerance_percent: Decimal = None
    ) -> bool:
        """
        Check if price change between two quotes is within tolerance.
        
        This is used to protect users from price slippage when executing
        USD-denominated transfers. If the price has moved more than the
        tolerance percentage, the transaction should be rejected.
        
        Args:
            original_quote: Original ETH quote amount
            new_quote: New ETH quote amount
            tolerance_percent: Maximum allowed price change percentage (default: from config)
            
        Returns:
            bool: True if price change is within tolerance, False otherwise
            
        Example:
            >>> check_price_tolerance(Decimal("0.045"), Decimal("0.0455"), Decimal("1.0"))
            True  # 1.11% change, within 1% tolerance
            >>> check_price_tolerance(Decimal("0.045"), Decimal("0.046"), Decimal("1.0"))
            False  # 2.22% change, exceeds 1% tolerance
        """
        # Use default tolerance if not provided
        if tolerance_percent is None:
            tolerance_percent = self.DEFAULT_PRICE_TOLERANCE_PERCENT
        
        # Handle edge case where original quote is zero
        if original_quote == 0:
            return new_quote == 0
        
        # Calculate absolute price change percentage
        price_change = abs(new_quote - original_quote)
        price_change_percent = (price_change / original_quote) * Decimal('100')
        
        # Check if within tolerance
        within_tolerance = price_change_percent <= tolerance_percent
        
        if not within_tolerance:
            logger.warning(
                f"Price change {price_change_percent:.2f}% exceeds tolerance {tolerance_percent}%. "
                f"Original: {original_quote}, New: {new_quote}"
            )
        
        return within_tolerance
    
    def _parse_eth_amount_from_response(self, response_data: Dict[str, Any]) -> Decimal:
        """
        Parse ETH amount from Skip API response.
        
        The response structure may vary, so this method handles different formats.
        Expected response contains ETH amount in wei (18 decimals).
        
        Args:
            response_data: Raw API response dictionary
            
        Returns:
            Decimal: ETH amount
            
        Raises:
            ValueError: If response format is invalid or ETH amount not found
        """
        # Try to extract ETH amount from various possible response structures
        # This is based on Skip API documentation and may need adjustment
        
        # Check for amount_out field (most common)
        if 'amount_out' in response_data:
            eth_units = int(response_data['amount_out'])
            return self.convert_eth_units_to_eth(eth_units)
        
        # Check for nested structure
        if 'route' in response_data and 'amount_out' in response_data['route']:
            eth_units = int(response_data['route']['amount_out'])
            return self.convert_eth_units_to_eth(eth_units)
        
        # Check for operations array
        if 'operations' in response_data and len(response_data['operations']) > 0:
            last_operation = response_data['operations'][-1]
            if 'amount_out' in last_operation:
                eth_units = int(last_operation['amount_out'])
                return self.convert_eth_units_to_eth(eth_units)
        
        # If we can't find the ETH amount, raise an error
        logger.error(f"Could not parse ETH amount from response: {response_data}")
        raise ValueError("Invalid Skip API response format - ETH amount not found")
