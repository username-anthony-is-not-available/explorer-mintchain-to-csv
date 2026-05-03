from writers import CoinTrackerWriter

def write_transaction_data_to_cointracker_csv(output_file: str, transaction_data: list) -> None:
    CoinTrackerWriter().write(output_file, transaction_data)
