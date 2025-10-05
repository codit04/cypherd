# Test Accounts for Mock Web3 Wallet Frontend Validation

## Test Account 1: New Wallet Creation

**Action**: Click "Create Wallet" on the welcome page

**Test Steps**:
1. Enter password: `testpassword123`
2. Confirm password: `testpassword123`
3. Click "Create Wallet"
4. **Save the mnemonic phrase displayed** (you'll need it for testing import)
5. Check the "I have written down my mnemonic phrase" checkbox
6. Click "Continue to Wallet"

**Expected Results**:
- Wallet ID is displayed
- 12-word mnemonic phrase is shown
- First account is created with random balance (1.0-10.0 ETH)
- After confirmation, you're redirected to the dashboard

---

## Test Account 2: Import Existing Wallet

**Pre-generated Test Mnemonic**:
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
```

**Test Steps**:
1. Click "Import Wallet" on the welcome page
2. Enter the mnemonic phrase above
3. Enter password: `password12345`
4. Confirm password: `password12345`
5. Click "Import Wallet"

**Expected Results**:
- Wallet is restored successfully
- Wallet ID: `f0e4c2f7-6b8a-4c9d-8e1f-3a5b7c9d0e2f` (deterministic from mnemonic)
- If wallet exists in DB, existing accounts are loaded
- If new, a new wallet entry is created

**Note**: This is a standard BIP39 test mnemonic. The wallet ID will be deterministic based on the mnemonic.

---

## Test Account 3: Unlock Existing Wallet

**Prerequisites**: First create a wallet using Test Account 1, then lock it

**Test Steps**:
1. After creating a wallet, note the Wallet ID
2. Click "Lock Wallet" (if available in dashboard)
3. Return to welcome page
4. In the "Unlock Wallet" section, enter:
   - Wallet ID: `[your wallet ID from step 1]`
   - Password: `testpassword123`
5. Click "Unlock Wallet"

**Expected Results**:
- Wallet unlocks successfully
- You're redirected to the dashboard
- All accounts and balances are displayed

---

## Test Account 4: Invalid Mnemonic

**Test Steps**:
1. Click "Import Wallet"
2. Enter invalid mnemonic: `invalid test words that are not valid mnemonic phrase at all`
3. Enter password: `password123`
4. Confirm password: `password123`
5. Click "Import Wallet"

**Expected Results**:
- Error message displayed: "Invalid mnemonic phrase" or similar
- Wallet is not created
- User remains on import page

---

## Test Account 5: Password Validation

**Test Steps**:
1. Click "Create Wallet"
2. Enter password: `short` (less than 8 characters)
3. Confirm password: `short`
4. Click "Create Wallet"

**Expected Results**:
- Error message: "Password must be at least 8 characters long"
- Wallet is not created

---

## Test Account 6: Password Mismatch

**Test Steps**:
1. Click "Create Wallet"
2. Enter password: `testpassword123`
3. Confirm password: `differentpassword`
4. Click "Create Wallet"

**Expected Results**:
- Error message: "Passwords do not match"
- Wallet is not created

---

## Additional Test Mnemonics

Here are more valid BIP39 test mnemonics you can use:

### Test Mnemonic 2:
```
legal winner thank year wave sausage worth useful legal winner thank yellow
```

### Test Mnemonic 3:
```
letter advice cage absurd amount doctor acoustic avoid letter advice cage above
```

### Test Mnemonic 4:
```
zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong
```

---

## Backend Validation

To verify the backend is working correctly, you can also test the API directly:

### Create Wallet via API:
```bash
curl -X POST http://localhost:8000/api/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"password": "testpassword123"}'
```

### Restore Wallet via API:
```bash
curl -X POST http://localhost:8000/api/wallet/restore \
  -H "Content-Type: application/json" \
  -d '{
    "mnemonic": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
    "password": "password12345"
  }'
```

### Authenticate Wallet via API:
```bash
curl -X POST http://localhost:8000/api/wallet/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_id": "[your-wallet-id]",
    "password": "testpassword123"
  }'
```

---

## Testing Checklist

- [ ] Create new wallet with valid password
- [ ] Mnemonic phrase is displayed correctly (12 words)
- [ ] Copy mnemonic button works
- [ ] Confirmation checkbox is required
- [ ] First account shows balance between 1.0-10.0 ETH
- [ ] Import wallet with valid mnemonic
- [ ] Import wallet with invalid mnemonic (error handling)
- [ ] Password validation (minimum 8 characters)
- [ ] Password mismatch validation
- [ ] Unlock existing wallet with correct credentials
- [ ] Unlock with incorrect password (error handling)
- [ ] Session state persists wallet_id and authenticated status
- [ ] Navigation between pages works correctly
- [ ] Loading indicators appear during API calls
- [ ] Error messages are user-friendly

---

## Notes

- Make sure the backend is running at `http://localhost:8000` before testing
- The database should be properly initialized
- Check browser console for any JavaScript errors
- Check backend logs for API errors
- Session state is stored in Streamlit's session, so refreshing the page will reset it
