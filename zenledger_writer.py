from writers import ZenLedgerWriter

def map_transaction_type(tx: dict) -> str:
    return ZenLedgerWriter()._map_type(tx)

def write_transaction_data_to_zenledger_csv(output_file: str, transaction_data: list) -> None:
    ZenLedgerWriter().write(output_file, transaction_data)
