from typing import Any, Optional, Union
from pydantic import BaseModel, Field, AliasChoices, model_validator
from enum import Enum


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


class RawTransaction(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    value: str
    gasUsed: Optional[str] = Field(None, validation_alias=AliasChoices("gasUsed", "gas"))
    gasPrice: Optional[str] = None


class RawTokenTransfer(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    total: Total
    token: Token
    tokenDecimal: str
    contractAddress: str


class RawNFTTransfer(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    tokenID: str
    tokenName: str
    tokenSymbol: str
    tokenDecimal: Optional[str] = "0"


class Raw1155Transfer(BaseModel):
    hash: str = Field(..., validation_alias=AliasChoices("hash", "transactionHash"))
    timeStamp: str
    from_address: Address = Field(..., alias="from")
    to_address: Address = Field(..., alias="to")
    tokenID: str
    tokenValue: str
    tokenName: str
    tokenSymbol: str


class Transaction(BaseModel):
    date: str = Field(..., alias="Date")
    timestamp: int = Field(..., exclude=True)
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
