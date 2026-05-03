import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv
import io

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derives a Fernet key from a password and salt.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_path: str, password: str) -> None:
    """
    Encrypts a file and replaces it with the encrypted version.
    Prepends the salt to the file.
    """
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)
    
    with open(file_path, "wb") as f:
        f.write(salt + encrypted_data)

def decrypt_and_load_env(encrypted_file_path: str, password: str) -> bool:
    """
    Decrypts the file in memory and loads it into environment variables.
    """
    try:
        with open(encrypted_file_path, "rb") as f:
            salt = f.read(16)
            encrypted_data = f.read()

        key = generate_key_from_password(password, salt)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)

        # Load into environment variables
        env_file = io.StringIO(decrypted_data.decode())
        load_dotenv(stream=env_file)
        return True
    except Exception:
        return False
