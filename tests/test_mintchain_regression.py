import pytest
from models import RawTransaction, RawNFTTransfer, RawTokenTransfer, Raw1155Transfer
from transaction_categorization import categorize_transaction

# Mock Data Constants (Golden Masters)
# Note: These are representative hashes as real-world ones were not found in search,
# but they represent the correct structure and address mapping.
HASH_SWAP_MINTCHAIN = "0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef"
HASH_SWAP_PANCAKE = "0xabcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
HASH_BRIDGE_OUT = "0x1234567890123456789012345678901234567890123456789012345678901234"
HASH_BRIDGE_IN = "0x4321098765432109876543210987654321098765432109876543210987654321"
HASH_NFT_MINT = "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
HASH_STAKING = "0x5555555555555555555555555555555555555555555555555555555555555555"

def create_raw_tx(tx_hash, to_address, from_address="0xuseraddress12345678901234567890123456", value="0"):
    return RawTransaction.model_validate({
        "hash": tx_hash,
        "timeStamp": "1710000000",
        "from": {"hash": from_address},
        "to": {"hash": to_address},
        "value": value,
        "gasUsed": "21000",
        "gasPrice": "100000000"
    })

def create_raw_nft_transfer(tx_hash, from_address, to_address, token_symbol="NFT", token_id="1"):
    return RawNFTTransfer.model_validate({
        "hash": tx_hash,
        "timeStamp": "1710000000",
        "from": {"hash": from_address},
        "to": {"hash": to_address},
        "tokenID": token_id,
        "tokenName": "NFT Name",
        "tokenSymbol": token_symbol,
        "tokenDecimal": "0"
    })

@pytest.mark.parametrize("tx_hash, to_address, expected_label", [
    (HASH_SWAP_MINTCHAIN, "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a", "swap"), # Mintchain SwapRouter
    (HASH_SWAP_PANCAKE, "0x13f4395944a2353e81e2975988e65a20da192bc7", "swap"),   # PancakeSwap V3 Router
    ("0x1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff", "0x1b81d7788448729965a3bc5573479e00a9075306", "swap"), # MintChain DEX Router
])
def test_mintchain_dex_swaps(tx_hash, to_address, expected_label):
    tx = create_raw_tx(tx_hash, to_address)
    assert categorize_transaction(tx, chain="mintchain") == expected_label

@pytest.mark.parametrize("tx_hash, bridge_address, is_outgoing, expected_label", [
    (HASH_BRIDGE_OUT, "0x4200000000000000000000000000000000000010", True, "bridge"), # L2StandardBridge
    (HASH_BRIDGE_IN, "0x4200000000000000000000000000000000000010", False, "bridge"),
    ("0x2222222222222222222222222222222222222222222222222222222222222222", "0x4200000000000000000000000000000000000014", True, "bridge"), # L2ERC721Bridge
    ("0x3333333333333333333333333333333333333333333333333333333333333333", "0x4200000000000000000000000000000000000007", True, "bridge"), # L2CrossDomainMessenger
    ("0x4444444444444444444444444444444444444444444444444444444444444444", "0x4200000000000000000000000000000000000016", True, "bridge"), # L2ToL1MessagePasser
])
def test_mintchain_bridge_transactions(tx_hash, bridge_address, is_outgoing, expected_label):
    if is_outgoing:
        tx = create_raw_tx(tx_hash, bridge_address)
    else:
        tx = create_raw_tx(tx_hash, "0xuseraddress", from_address=bridge_address)

    assert categorize_transaction(tx, chain="mintchain") == expected_label

def test_mintchain_nft_mint():
    # NFT Mint is characterized by an incoming transfer from 0x0
    # In practice, this would be part of a larger transaction, but the categorization
    # for individual transfers relies on the transfer data itself.
    mint_transfer = create_raw_nft_transfer(HASH_NFT_MINT, "0x0000000000000000000000000000000000000000", "0xuseraddress")
    assert categorize_transaction(mint_transfer, chain="mintchain") == "mint"

def test_mintchain_staking():
    staking_contract = "0x2e8697157321681285227092892994469e38f921"
    tx = create_raw_tx(HASH_STAKING, staking_contract)
    assert categorize_transaction(tx, chain="mintchain") == "staking"

def test_mintchain_cost():
    # A transaction with 0 value and gas paid is 'cost' if not a specialized type
    tx = create_raw_tx("0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc", "0xrandomcontractaddress", value="0")
    assert categorize_transaction(tx, chain="mintchain") == "cost"

def test_mintchain_simple_transfer():
    tx = create_raw_tx("0x5555555555555555555555555555555555555555555555555555555555555555", "0xrecipientaddress", value="1000000000000000000")
    assert categorize_transaction(tx, chain="mintchain") == "transfer"
