from writers import KoinlyWriter

def write_transaction_data_to_koinly_csv(output_file: str, transaction_data: list, chain: str = "mintchain") -> None:
    KoinlyWriter().write(output_file, transaction_data, chain=chain)
