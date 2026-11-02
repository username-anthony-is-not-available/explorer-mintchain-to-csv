import os
import pytest
from encrypt_env import main as encrypt_env_main
from security_utils import (
    decrypt_and_load_env,
    decrypt_file,
    encrypt_file,
)


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


def test_decrypt_and_load_env_short_file(tmp_path):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "wb") as f:
        f.write(b"too_short")

    success = decrypt_and_load_env(env_path, "any_password")
    assert success is False


def test_decrypt_and_load_env_nonexistent():
    success = decrypt_and_load_env("nonexistent_path_to_file", "pwd")
    assert success is False


def test_decrypt_file_in_place(tmp_path):
    env_path = os.path.join(tmp_path, ".env")
    password = "secret_password"
    original_content = "SECRET_TOKEN=xyz987\nPORT=8080\n"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(original_content)

    encrypt_file(env_path, password)

    # File is now encrypted
    with open(env_path, "rb") as f:
        encrypted_bytes = f.read()
        assert b"SECRET_TOKEN" not in encrypted_bytes

    # Decrypt in place
    success = decrypt_file(env_path, password)
    assert success is True

    with open(env_path, "r", encoding="utf-8") as f:
        decrypted_content = f.read()
    assert decrypted_content == original_content


def test_decrypt_file_to_output_path(tmp_path):
    env_path = os.path.join(tmp_path, ".env.enc")
    out_path = os.path.join(tmp_path, ".env.decrypted")
    password = "secret_password"
    original_content = "KEY=value\n"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(original_content)

    encrypt_file(env_path, password)

    success = decrypt_file(env_path, password, output_path=out_path)
    assert success is True

    # Check output file has original content
    with open(out_path, "r", encoding="utf-8") as f:
        assert f.read() == original_content

    # Original file is still encrypted
    with open(env_path, "rb") as f:
        assert b"KEY=value" not in f.read()


def test_decrypt_file_wrong_password(tmp_path):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("KEY=secret")

    encrypt_file(env_path, "correct_password")

    success = decrypt_file(env_path, "wrong_password")
    assert success is False


def test_decrypt_file_short_file(tmp_path):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "wb") as f:
        f.write(b"short")

    success = decrypt_file(env_path, "password")
    assert success is False


def test_decrypt_file_nonexistent():
    success = decrypt_file("nonexistent_path_to_file", "pwd")
    assert success is False


def test_encrypt_env_cli_encrypt_success(tmp_path, capsys):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("API_KEY=12345")

    ret = encrypt_env_main(["--password", "test_pass", "--file", env_path])
    assert ret == 0

    captured = capsys.readouterr()
    assert "encrypted successfully" in captured.out

    with open(env_path, "rb") as f:
        assert b"API_KEY" not in f.read()


def test_encrypt_env_cli_decrypt_success(tmp_path, capsys):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("API_KEY=12345")

    encrypt_file(env_path, "test_pass")

    ret = encrypt_env_main(["--password", "test_pass", "--file", env_path, "--decrypt"])
    assert ret == 0

    captured = capsys.readouterr()
    assert "decrypted successfully" in captured.out

    with open(env_path, "r", encoding="utf-8") as f:
        assert f.read() == "API_KEY=12345"


def test_encrypt_env_cli_decrypt_to_output(tmp_path, capsys):
    env_path = os.path.join(tmp_path, ".env.enc")
    out_path = os.path.join(tmp_path, ".env.plain")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("API_KEY=12345")

    encrypt_file(env_path, "test_pass")

    ret = encrypt_env_main([
        "--password", "test_pass",
        "--file", env_path,
        "--decrypt",
        "--output", out_path
    ])
    assert ret == 0

    captured = capsys.readouterr()
    assert "decrypted successfully" in captured.out

    with open(out_path, "r", encoding="utf-8") as f:
        assert f.read() == "API_KEY=12345"


def test_encrypt_env_cli_file_not_found(capsys):
    ret = encrypt_env_main(["--password", "test_pass", "--file", "does_not_exist.env"])
    assert ret == 1

    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_encrypt_env_cli_decrypt_failure(tmp_path, capsys):
    env_path = os.path.join(tmp_path, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("API_KEY=12345")

    encrypt_file(env_path, "test_pass")

    ret = encrypt_env_main(["--password", "wrong_pass", "--file", env_path, "--decrypt"])
    assert ret == 1

    captured = capsys.readouterr()
    assert "Failed to decrypt" in captured.err


def test_encrypt_env_cli_requires_password():
    with pytest.raises(SystemExit):
        encrypt_env_main([])
