import argparse
import os
from security_utils import encrypt_file

def main():
    parser = argparse.ArgumentParser(description="Encrypt your .env file.")
    parser.add_argument("--password", required=True, help="Password to encrypt the .env file.")
    parser.add_argument("--file", default=".env", help="Path to the file to encrypt.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"File {args.file} not found.")
        return
    
    encrypt_file(args.file, args.password)
    print(f"File {args.file} encrypted successfully.")

if __name__ == "__main__":
    main()
