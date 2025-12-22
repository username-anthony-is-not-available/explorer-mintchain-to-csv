from typing import Optional
from pydantic import BaseModel, Field

class Address(BaseModel):
    hash: str

class Token(BaseModel):
    symbol: str

class Total(BaseModel):
    value: str

class RawTransaction(BaseModel):
    hash: str
    timeStamp: str
    from_address: Address = Field(..., alias='from')
    to_address: Address = Field(..., alias='to')
    value: str
    gasUsed: str
    gasPrice: str

class RawTokenTransfer(BaseModel):
    hash: str
    timeStamp: str
    from_address: Address = Field(..., alias='from')
    to_address: Address = Field(..., alias='to')
    total: Total
    token: Token

class Transaction(BaseModel):
    date: str = Field(..., alias='Date')
    sent_amount: Optional[str] = Field(None, alias='Sent Amount')
    sent_currency: Optional[str] = Field(None, alias='Sent Currency')
    received_amount: Optional[str] = Field(None, alias='Received Amount')
    received_currency: Optional[str] = Field(None, alias='Received Currency')
    fee_amount: Optional[str] = Field(None, alias='Fee Amount')
    fee_currency: Optional[str] = Field(None, alias='Fee Currency')
    net_worth_amount: Optional[str] = Field(None, alias='Net Worth Amount')
    net_worth_currency: Optional[str] = Field(None, alias='Net Worth Currency')
    label: Optional[str] = Field(None, alias='Label')
    description: str = Field(..., alias='Description')
    tx_hash: str = Field(..., alias='TxHash')
