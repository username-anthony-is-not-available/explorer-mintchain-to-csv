from writers import JSONWriter

def write_transaction_data_to_json(output_file: str, transaction_data: list) -> None:
    JSONWriter().write(output_file, transaction_data)
