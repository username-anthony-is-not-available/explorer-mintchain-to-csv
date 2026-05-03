import os
from security_utils import encrypt_file, decrypt_and_load_env

def test_encryption_decryption(tmp_path):
    env_path = os.path.join(tmp_path, ".env")
    password = "test_password"
    content = "API_KEY=test_key_123\nOTHER_VAR=abc"
    
    with open(env_path, "w") as f:
        f.write(content)
    
    # Encrypt
    encrypt_file(env_path, password)
    
    # Verify it's not plain text anymore
    with open(env_path, "rb") as f:
        data = f.read()
        assert b"API_KEY" not in data
    
    # Decrypt and load
    # Clear env var first if it exists
    if "API_KEY" in os.environ:
        del os.environ["API_KEY"]
        
    success = decrypt_and_load_env(env_path, password)
    assert success is True
    assert os.getenv("API_KEY") == "test_key_123"
    assert os.getenv("OTHER_VAR") == "abc"

def test_decryption_failure(tmp_path):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "w") as f:
        f.write("API_KEY=test")
    
    encrypt_file(env_path, "correct_password")
    
    success = decrypt_and_load_env(env_path, "wrong_password")
    assert success is False
