from writers import CryptoTaxCalculatorWriter

def write_transaction_data_to_cryptotaxcalculator_csv(output_file: str, transaction_data: list) -> None:
    CryptoTaxCalculatorWriter().write(output_file, transaction_data)
