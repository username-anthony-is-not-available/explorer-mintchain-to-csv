from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Union
from pydantic import BaseModel, Field, AliasChoices, field_validator, model_validator
from enum import Enum


def _validate_unsigned_integer(value: str) -> str:
    if not value.isascii() or not value.isdigit():
        raise ValueError("must be a non-negative integer string")
    return value


def _validate_optional_unsigned_integer(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _validate_unsigned_integer(value)


def _validate_decimal_amount(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return value
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("must be a valid decimal amount") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("must be a finite, non-negative decimal amount")
    return value


class TransactionType(Enum):
    BRIDGE = "bridge"
    SWAP = "swap"
    MINT = "mint"
    BURN = "burn"
    NFT_TRANSFER = "nft_transfer"
    TOKEN_TRANSFER = "token_transfer"
    TRANSFER = "transfer"
    STAKING = "staking"
    AIRDROP = "airdrop"
    MINING = "mining"
    COST = "cost"
    LIQUIDITY_ADD = "liquidity_add"
    LIQUIDITY_REMOVE = "liquidity_remove"
    LEND = "lend"
    BORROW = "borrow"


class Address(BaseModel):
    hash: str

    @model_validator(mode="before")
    @classmethod
    def validate_address(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"hash": data}
        return data


class Token(BaseModel):
    symbol: str


class Total(BaseModel):
    value: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str) -> str:
        return _validate_unsigned_integer(value)


class RawTransaction(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    value: str
    gasUsed: Optional[str] = Field(None, validation_alias=AliasChoices("gasUsed", "gas"))
    gasPrice: Optional[str] = None

    @field_validator("timeStamp", "value")
    @classmethod
    def validate_integer_fields(cls, value: str) -> str:
        return _validate_unsigned_integer(value)

    @field_validator("gasUsed", "gasPrice")
    @classmethod
    def validate_optional_integer_fields(cls, value: Optional[str]) -> Optional[str]:
        return _validate_optional_unsigned_integer(value)


class RawTokenTransfer(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    total: Total
    token: Token
    tokenDecimal: str
    contractAddress: str

    @field_validator("tokenDecimal")
    @classmethod
    def validate_token_decimals(cls, value: str) -> str:
        return _validate_unsigned_integer(value)


class RawNFTTransfer(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    tokenID: str
    tokenName: str
    tokenSymbol: str
    tokenDecimal: Optional[str] = "0"

    @field_validator("tokenID")
    @classmethod
    def validate_token_id(cls, value: str) -> str:
        return _validate_unsigned_integer(value)

    @field_validator("tokenDecimal")
    @classmethod
    def validate_token_decimals(cls, value: Optional[str]) -> Optional[str]:
        return _validate_optional_unsigned_integer(value)


class Raw1155Transfer(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    tokenID: str
    tokenValue: str
    tokenName: str
    tokenSymbol: str

    @field_validator("tokenID", "tokenValue")
    @classmethod
    def validate_integer_fields(cls, value: str) -> str:
        return _validate_unsigned_integer(value)


class Transaction(BaseModel):
    date: str = Field(..., alias="Date")
    timestamp: int = Field(..., exclude=True, ge=0)
    sent_amount: Optional[str] = Field(None, alias="Sent Amount")
    sent_currency: Optional[str] = Field(None, alias="Sent Currency")
    received_amount: Optional[str] = Field(None, alias="Received Amount")
    received_currency: Optional[str] = Field(None, alias="Received Currency")
    fee_amount: Optional[str] = Field(None, alias="Fee Amount")
    fee_currency: Optional[str] = Field(None, alias="Fee Currency")
    net_worth_amount: Optional[str] = Field(None, alias="Net Worth Amount")
    net_worth_currency: Optional[str] = Field(None, alias="Net Worth Currency")
    label: Optional[Union[TransactionType, str]] = Field(None, alias="Label")
    description: str = Field(..., alias="Description")
    tx_hash: str = Field(..., alias="TxHash")

    @field_validator("sent_amount", "received_amount", "fee_amount", "net_worth_amount")
    @classmethod
    def validate_amount_fields(cls, value: Optional[str]) -> Optional[str]:
        return _validate_decimal_amount(value)

    @model_validator(mode="after")
    def check_amounts_and_currencies(self) -> "Transaction":
        if self.sent_amount and not self.sent_currency:
            raise ValueError("sent_currency must be provided if sent_amount is set")
        if self.received_amount and not self.received_currency:
            raise ValueError("received_currency must be provided if received_amount is set")
        return self

    @model_validator(mode="before")
    @classmethod
    def handle_label_enum(cls, data: Any) -> Any:
        if isinstance(data, dict) and "Label" in data:
            label = data["Label"]
            if isinstance(label, TransactionType):
                data["Label"] = label.value
        return data
