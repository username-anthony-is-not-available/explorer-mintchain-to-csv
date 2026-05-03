from writers import CSVWriter

def write_transaction_data_to_csv(output_file: str, transaction_data: list) -> None:
    CSVWriter().write(output_file, transaction_data)
