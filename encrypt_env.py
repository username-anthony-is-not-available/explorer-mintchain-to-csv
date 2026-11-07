import argparse
import os
import sys
from typing import Optional, Sequence
from security_utils import decrypt_file, encrypt_file


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt your .env file."
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password to encrypt or decrypt the file.",
    )
    parser.add_argument(
        "--file",
        default=".env",
        help="Path to the file to encrypt or decrypt (default: .env).",
    )
    parser.add_argument(
        "--decrypt",
        action="store_true",
        help="Decrypt the file instead of encrypting it.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output file path. Defaults to overwriting the target file.",
    )

    args = parser.parse_args(argv)

    if not os.path.exists(args.file):
        print(f"File {args.file} not found.", file=sys.stderr)
        return 1

    if args.decrypt:
        success = decrypt_file(args.file, args.password, output_path=args.output)
        if success:
            out_dest = args.output if args.output else args.file
            print(f"File {args.file} decrypted successfully to {out_dest}.")
            return 0
        else:
            print(f"Failed to decrypt {args.file}. Incorrect password or invalid file.", file=sys.stderr)
            return 1
    else:
        encrypt_file(args.file, args.password)
        print(f"File {args.file} encrypted successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
