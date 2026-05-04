"""Tests pour credentials_manager."""

import base64
import json
import os
import subprocess
import sys

import pytest

from credentials_manager import (
    batch_decode,
    batch_encode,
    check_password_strength,
    decode_credentials,
    decrypt_credentials,
    encode_credentials,
    encrypt_credentials,
    format_batch_decode,
    format_batch_encode,
    format_decoded,
    format_encoded,
    generate_key,
)


# --- encode_credentials ---


class TestEncode:
    def test_basic(self):
        result = encode_credentials("admin", "secret123")
        assert result == base64.b64encode(b"admin:secret123").decode()

    def test_empty_username(self):
        result = encode_credentials("", "password")
        decoded = base64.b64decode(result).decode()
        assert decoded == ":password"

    def test_empty_password(self):
        result = encode_credentials("user", "")
        decoded = base64.b64decode(result).decode()
        assert decoded == "user:"

    def test_both_empty(self):
        result = encode_credentials("", "")
        decoded = base64.b64decode(result).decode()
        assert decoded == ":"

    def test_special_characters(self):
        result = encode_credentials("user@domain.com", "p@ss:w0rd!#$")
        decoded = base64.b64decode(result).decode()
        assert decoded == "user@domain.com:p@ss:w0rd!#$"

    def test_unicode(self):
        result = encode_credentials("utilisateur", "môtdëpàsse")
        decoded = base64.b64decode(result).decode()
        assert decoded == "utilisateur:môtdëpàsse"

    def test_long_values(self):
        username = "a" * 1000
        password = "b" * 1000
        result = encode_credentials(username, password)
        decoded = base64.b64decode(result).decode()
        assert decoded == f"{username}:{password}"


# --- decode_credentials ---


class TestDecode:
    def test_basic(self):
        encoded = base64.b64encode(b"admin:secret123").decode()
        username, password = decode_credentials(encoded)
        assert username == "admin"
        assert password == "secret123"

    def test_empty_username(self):
        encoded = base64.b64encode(b":password").decode()
        username, password = decode_credentials(encoded)
        assert username == ""
        assert password == "password"

    def test_empty_password(self):
        encoded = base64.b64encode(b"user:").decode()
        username, password = decode_credentials(encoded)
        assert username == "user"
        assert password == ""

    def test_colon_in_password(self):
        encoded = base64.b64encode(b"user:pass:with:colons").decode()
        username, password = decode_credentials(encoded)
        assert username == "user"
        assert password == "pass:with:colons"

    def test_unicode(self):
        encoded = base64.b64encode("utilisateur:môtdëpàsse".encode()).decode()
        username, password = decode_credentials(encoded)
        assert username == "utilisateur"
        assert password == "môtdëpàsse"

    def test_invalid_base64(self):
        with pytest.raises(ValueError, match="base64 invalides"):
            decode_credentials("not-valid-base64!!!")

    def test_missing_separator(self):
        encoded = base64.b64encode(b"nocolonhere").decode()
        with pytest.raises(ValueError, match="séparateur"):
            decode_credentials(encoded)


# --- roundtrip ---


class TestRoundtrip:
    @pytest.mark.parametrize(
        "username,password",
        [
            ("admin", "secret"),
            ("", "onlypass"),
            ("onlyuser", ""),
            ("user@mail.com", "p@ss:w0rd!"),
            ("utilisateur", "àéîöü"),
        ],
    )
    def test_encode_decode_roundtrip(self, username, password):
        encoded = encode_credentials(username, password)
        decoded_user, decoded_pass = decode_credentials(encoded)
        assert decoded_user == username
        assert decoded_pass == password


# --- CLI ---


class TestCLI:
    def run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            capture_output=True,
            text=True,
        )
        return result

    def test_encode_cli(self):
        result = self.run_cli("encode", "-u", "admin", "-p", "secret123")
        assert result.returncode == 0
        assert result.stdout.strip() == base64.b64encode(b"admin:secret123").decode()

    def test_decode_cli(self):
        token = base64.b64encode(b"admin:secret123").decode()
        result = self.run_cli("decode", token)
        assert result.returncode == 0
        assert "admin" in result.stdout
        assert "secret123" in result.stdout

    def test_decode_cli_invalid(self):
        result = self.run_cli("decode", "not-valid!!!")
        assert result.returncode == 1
        assert "Erreur" in result.stderr

    def test_help(self):
        result = self.run_cli("--help")
        assert result.returncode == 0
        assert "encode" in result.stdout
        assert "decode" in result.stdout

    def test_encode_format_json(self):
        result = self.run_cli("encode", "-u", "admin", "-p", "secret", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "encoded" in data

    def test_encode_format_env(self):
        result = self.run_cli("encode", "-u", "admin", "-p", "secret", "--format", "env")
        assert result.returncode == 0
        assert result.stdout.strip().startswith("CREDENTIALS=")

    def test_decode_format_json(self):
        token = base64.b64encode(b"admin:secret").decode()
        result = self.run_cli("decode", token, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["username"] == "admin"
        assert data["password"] == "secret"

    def test_decode_format_env(self):
        token = base64.b64encode(b"admin:secret").decode()
        result = self.run_cli("decode", token, "--format", "env")
        assert result.returncode == 0
        assert "USERNAME=admin" in result.stdout
        assert "PASSWORD=secret" in result.stdout

    def test_encode_output_file(self, tmp_path):
        out = tmp_path / "encoded.txt"
        result = self.run_cli("encode", "-u", "admin", "-p", "secret", "-o", str(out))
        assert result.returncode == 0
        assert out.read_text(encoding="utf-8").strip() == base64.b64encode(b"admin:secret").decode()

    def test_decode_output_file(self, tmp_path):
        token = base64.b64encode(b"admin:secret").decode()
        out = tmp_path / "decoded.txt"
        result = self.run_cli("decode", token, "-o", str(out))
        assert result.returncode == 0
        content = out.read_text(encoding="utf-8")
        assert "admin" in content
        assert "secret" in content


# --- format helpers ---


class TestFormat:
    def test_format_encoded_text(self):
        assert format_encoded("abc123") == "abc123"

    def test_format_encoded_json(self):
        result = json.loads(format_encoded("abc123", "json"))
        assert result == {"encoded": "abc123"}

    def test_format_encoded_env(self):
        assert format_encoded("abc123", "env") == "CREDENTIALS=abc123"

    def test_format_decoded_text(self):
        result = format_decoded("admin", "secret")
        assert "admin" in result
        assert "secret" in result

    def test_format_decoded_json(self):
        result = json.loads(format_decoded("admin", "secret", "json"))
        assert result == {"username": "admin", "password": "secret"}

    def test_format_decoded_env(self):
        result = format_decoded("admin", "secret", "env")
        assert "USERNAME=admin" in result
        assert "PASSWORD=secret" in result


# --- batch ---


class TestBatch:
    def test_batch_encode(self, tmp_path):
        f = tmp_path / "creds.txt"
        f.write_text("admin:secret\nuser2:pass2\n", encoding="utf-8")
        results = batch_encode(str(f))
        assert len(results) == 2
        assert results[0]["username"] == "admin"
        assert results[1]["username"] == "user2"

    def test_batch_encode_skips_comments_and_blanks(self, tmp_path):
        f = tmp_path / "creds.txt"
        f.write_text("# comment\n\nadmin:secret\n", encoding="utf-8")
        results = batch_encode(str(f))
        assert len(results) == 1

    def test_batch_encode_missing_colon(self, tmp_path):
        f = tmp_path / "creds.txt"
        f.write_text("nocolon\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Ligne 1"):
            batch_encode(str(f))

    def test_batch_encode_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            batch_encode("nonexistent_file.txt")

    def test_batch_decode(self, tmp_path):
        tokens = [
            base64.b64encode(b"admin:secret").decode(),
            base64.b64encode(b"user2:pass2").decode(),
        ]
        f = tmp_path / "tokens.txt"
        f.write_text("\n".join(tokens) + "\n", encoding="utf-8")
        results = batch_decode(str(f))
        assert len(results) == 2
        assert results[0]["username"] == "admin"
        assert results[1]["password"] == "pass2"

    def test_batch_decode_skips_comments_and_blanks(self, tmp_path):
        token = base64.b64encode(b"admin:secret").decode()
        f = tmp_path / "tokens.txt"
        f.write_text(f"# comment\n\n{token}\n", encoding="utf-8")
        results = batch_decode(str(f))
        assert len(results) == 1

    def test_batch_decode_invalid_line(self, tmp_path):
        f = tmp_path / "tokens.txt"
        f.write_text("not-valid!!!\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Ligne 1"):
            batch_decode(str(f))

    def test_format_batch_encode_json(self):
        results = [{"username": "admin", "encoded": "abc"}]
        parsed = json.loads(format_batch_encode(results, "json"))
        assert parsed == results

    def test_format_batch_encode_env(self):
        results = [{"username": "admin", "encoded": "abc"}]
        output = format_batch_encode(results, "env")
        assert "CREDENTIALS=abc" in output

    def test_format_batch_decode_json(self):
        results = [{"username": "admin", "password": "secret"}]
        parsed = json.loads(format_batch_decode(results, "json"))
        assert parsed == results

    def test_format_batch_decode_text(self):
        results = [{"username": "admin", "password": "secret"}]
        assert format_batch_decode(results) == "admin:secret"


# --- CLI batch ---


class TestCLIBatch:
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            capture_output=True,
            text=True,
        )

    def test_batch_encode_cli(self, tmp_path):
        f = tmp_path / "creds.txt"
        f.write_text("admin:secret\nuser2:pass2\n", encoding="utf-8")
        result = self.run_cli("encode", "-f", str(f))
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        assert len(lines) == 2

    def test_batch_encode_cli_json(self, tmp_path):
        f = tmp_path / "creds.txt"
        f.write_text("admin:secret\n", encoding="utf-8")
        result = self.run_cli("encode", "-f", str(f), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert data[0]["username"] == "admin"

    def test_batch_decode_cli(self, tmp_path):
        token = base64.b64encode(b"admin:secret").decode()
        f = tmp_path / "tokens.txt"
        f.write_text(f"{token}\n", encoding="utf-8")
        result = self.run_cli("decode", "-f", str(f))
        assert result.returncode == 0
        assert "admin:secret" in result.stdout

    def test_batch_decode_cli_json(self, tmp_path):
        token = base64.b64encode(b"admin:secret").decode()
        f = tmp_path / "tokens.txt"
        f.write_text(f"{token}\n", encoding="utf-8")
        result = self.run_cli("decode", "-f", str(f), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data[0]["username"] == "admin"

    def test_batch_encode_cli_output_file(self, tmp_path):
        f = tmp_path / "creds.txt"
        f.write_text("admin:secret\n", encoding="utf-8")
        out = tmp_path / "result.txt"
        result = self.run_cli("encode", "-f", str(f), "-o", str(out))
        assert result.returncode == 0
        assert out.read_text(encoding="utf-8").strip() != ""

    def test_batch_encode_cli_file_not_found(self):
        result = self.run_cli("encode", "-f", "nonexistent.txt")
        assert result.returncode == 1
        assert "Erreur" in result.stderr


# --- stdin ---


class TestStdin:
    def run_cli_stdin(self, stdin_data, *args):
        return subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            input=stdin_data,
            capture_output=True,
            text=True,
        )

    def test_encode_stdin(self):
        result = self.run_cli_stdin("admin:secret\n", "encode")
        assert result.returncode == 0
        assert result.stdout.strip() == base64.b64encode(b"admin:secret").decode()

    def test_decode_stdin(self):
        token = base64.b64encode(b"admin:secret").decode()
        result = self.run_cli_stdin(f"{token}\n", "decode")
        assert result.returncode == 0
        assert "admin:secret" in result.stdout

    def test_encode_stdin_multiple(self):
        result = self.run_cli_stdin("admin:secret\nuser2:pass2\n", "encode")
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        assert len(lines) == 2

    def test_decode_stdin_multiple(self):
        t1 = base64.b64encode(b"admin:secret").decode()
        t2 = base64.b64encode(b"user2:pass2").decode()
        result = self.run_cli_stdin(f"{t1}\n{t2}\n", "decode")
        assert result.returncode == 0
        assert "admin:secret" in result.stdout
        assert "user2:pass2" in result.stdout

    def test_encode_stdin_json(self):
        result = self.run_cli_stdin("admin:secret\n", "encode", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert data[0]["username"] == "admin"

    def test_encode_stdin_pipe_roundtrip(self):
        encode = subprocess.run(
            [sys.executable, "credentials_manager.py", "encode"],
            input="admin:secret\n",
            capture_output=True,
            text=True,
        )
        decode = subprocess.run(
            [sys.executable, "credentials_manager.py", "decode"],
            input=encode.stdout,
            capture_output=True,
            text=True,
        )
        assert decode.returncode == 0
        assert "admin:secret" in decode.stdout

    def test_encode_stdin_skips_comments(self):
        result = self.run_cli_stdin("# comment\n\nadmin:secret\n", "encode")
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        assert len(lines) == 1

    def test_decode_stdin_invalid(self):
        result = self.run_cli_stdin("not-valid!!!\n", "decode")
        assert result.returncode == 1
        assert "Erreur" in result.stderr


# --- alternative encodings ---


class TestAlternativeEncodings:
    @pytest.mark.parametrize("encoding", ["base64", "base32", "hex", "base85"])
    def test_roundtrip(self, encoding):
        encoded = encode_credentials("admin", "secret", encoding)
        username, password = decode_credentials(encoded, encoding)
        assert username == "admin"
        assert password == "secret"

    def test_base32_output(self):
        result = encode_credentials("admin", "secret", "base32")
        assert result == base64.b32encode(b"admin:secret").decode()

    def test_hex_output(self):
        result = encode_credentials("admin", "secret", "hex")
        assert result == b"admin:secret".hex()

    def test_base85_output(self):
        result = encode_credentials("admin", "secret", "base85")
        assert result == base64.b85encode(b"admin:secret").decode()

    def test_decode_wrong_encoding_raises(self):
        encoded = encode_credentials("admin", "secret", "base64")
        with pytest.raises(ValueError):
            decode_credentials(encoded, "base32")

    @pytest.mark.parametrize("encoding", ["base32", "hex", "base85"])
    def test_unicode_roundtrip(self, encoding):
        encoded = encode_credentials("user", "môtdëpàsse", encoding)
        u, p = decode_credentials(encoded, encoding)
        assert u == "user"
        assert p == "môtdëpàsse"

    @pytest.mark.parametrize("encoding", ["base32", "hex", "base85"])
    def test_batch_encode_with_encoding(self, tmp_path, encoding):
        f = tmp_path / "creds.txt"
        f.write_text("admin:secret\n", encoding="utf-8")
        results = batch_encode(str(f), encoding)
        assert len(results) == 1
        u, p = decode_credentials(results[0]["encoded"], encoding)
        assert u == "admin"
        assert p == "secret"


class TestAlternativeEncodingsCLI:
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            capture_output=True,
            text=True,
        )

    @pytest.mark.parametrize("encoding", ["base32", "hex", "base85"])
    def test_encode_decode_cli(self, encoding):
        enc = self.run_cli(
            "encode", "-u", "admin", "-p", "secret", "--encoding", encoding
        )
        assert enc.returncode == 0
        token = enc.stdout.strip()
        dec = self.run_cli("decode", token, "--encoding", encoding)
        assert dec.returncode == 0
        assert "admin" in dec.stdout
        assert "secret" in dec.stdout


# --- password strength ---


class TestPasswordStrength:
    def test_weak_password(self):
        warnings = check_password_strength("ab")
        assert len(warnings) >= 2
        assert any("Longueur" in w for w in warnings)

    def test_no_uppercase(self):
        warnings = check_password_strength("abcdefgh1!")
        assert any("majuscule" in w for w in warnings)

    def test_no_lowercase(self):
        warnings = check_password_strength("ABCDEFGH1!")
        assert any("minuscule" in w for w in warnings)

    def test_no_digit(self):
        warnings = check_password_strength("Abcdefgh!")
        assert any("chiffre" in w for w in warnings)

    def test_no_special(self):
        warnings = check_password_strength("Abcdefgh1")
        assert any("sp" in w for w in warnings)

    def test_strong_password(self):
        warnings = check_password_strength("Str0ng!Pass")
        assert warnings == []

    def test_empty_password(self):
        warnings = check_password_strength("")
        assert len(warnings) >= 1


class TestPasswordStrengthCLI:
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            capture_output=True,
            text=True,
        )

    def test_check_password_weak(self):
        result = self.run_cli(
            "encode", "-u", "admin", "-p", "ab", "--check-password"
        )
        assert result.returncode == 0
        assert result.stdout.strip() != ""
        assert "Longueur" in result.stderr

    def test_check_password_strong(self):
        result = self.run_cli(
            "encode", "-u", "admin", "-p", "Str0ng!Pass",
            "--check-password",
        )
        assert result.returncode == 0
        assert result.stderr == ""


# --- YAML format ---


class TestYAMLFormat:
    def test_format_encoded_yaml(self):
        result = format_encoded("abc123", "yaml")
        assert "encoded: abc123" in result

    def test_format_decoded_yaml(self):
        result = format_decoded("admin", "secret", "yaml")
        assert "username: admin" in result
        assert "password: secret" in result

    def test_format_decoded_yaml_special_chars(self):
        result = format_decoded("admin", "p@ss:word!", "yaml")
        assert "password:" in result
        assert "p@ss:word!" in result

    def test_format_batch_encode_yaml(self):
        results = [{"username": "admin", "encoded": "abc"}]
        output = format_batch_encode(results, "yaml")
        assert "- username: admin" in output
        assert "  encoded: abc" in output

    def test_format_batch_decode_yaml(self):
        results = [{"username": "admin", "password": "secret"}]
        output = format_batch_decode(results, "yaml")
        assert "- username: admin" in output
        assert "  password: secret" in output


class TestYAMLFormatCLI:
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            capture_output=True,
            text=True,
        )

    def test_encode_yaml(self):
        result = self.run_cli(
            "encode", "-u", "admin", "-p", "secret", "--format", "yaml"
        )
        assert result.returncode == 0
        assert "encoded:" in result.stdout

    def test_decode_yaml(self):
        token = base64.b64encode(b"admin:secret").decode()
        result = self.run_cli("decode", token, "--format", "yaml")
        assert result.returncode == 0
        assert "username: admin" in result.stdout
        assert "password: secret" in result.stdout


# --- Fernet encryption ---


class TestFernet:
    def test_generate_key(self):
        key = generate_key()
        assert len(key) == 44
        assert key.endswith("=")

    def test_generate_key_unique(self):
        k1 = generate_key()
        k2 = generate_key()
        assert k1 != k2

    def test_encrypt_decrypt_roundtrip(self):
        key = generate_key()
        token = encrypt_credentials("admin", "secret", key)
        username, password = decrypt_credentials(token, key)
        assert username == "admin"
        assert password == "secret"

    def test_encrypt_decrypt_special_chars(self):
        key = generate_key()
        token = encrypt_credentials("user@mail.com", "p@ss:w0rd!", key)
        u, p = decrypt_credentials(token, key)
        assert u == "user@mail.com"
        assert p == "p@ss:w0rd!"

    def test_encrypt_decrypt_unicode(self):
        key = generate_key()
        token = encrypt_credentials("utilisateur", "môtdëpàsse", key)
        u, p = decrypt_credentials(token, key)
        assert u == "utilisateur"
        assert p == "môtdëpàsse"

    def test_decrypt_wrong_key(self):
        key1 = generate_key()
        key2 = generate_key()
        token = encrypt_credentials("admin", "secret", key1)
        with pytest.raises(ValueError, match="invalide"):
            decrypt_credentials(token, key2)

    def test_decrypt_invalid_token(self):
        key = generate_key()
        with pytest.raises(ValueError, match="invalide"):
            decrypt_credentials("not-a-valid-token", key)

    def test_encrypt_empty_username(self):
        key = generate_key()
        token = encrypt_credentials("", "secret", key)
        u, p = decrypt_credentials(token, key)
        assert u == ""
        assert p == "secret"


class TestFernetCLI:
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "credentials_manager.py", *args],
            capture_output=True,
            text=True,
        )

    def test_keygen_cli(self):
        result = self.run_cli("keygen")
        assert result.returncode == 0
        key = result.stdout.strip()
        assert len(key) == 44

    def test_keygen_output_file(self, tmp_path):
        out = tmp_path / "key.txt"
        result = self.run_cli("keygen", "-o", str(out))
        assert result.returncode == 0
        key = out.read_text(encoding="utf-8").strip()
        assert len(key) == 44

    def test_encrypt_decrypt_cli(self):
        keygen = self.run_cli("keygen")
        key = keygen.stdout.strip()
        enc = self.run_cli(
            "encrypt", "-u", "admin", "-p", "secret", f"--key={key}"
        )
        assert enc.returncode == 0
        token = enc.stdout.strip()
        dec = self.run_cli("decrypt", token, f"--key={key}")
        assert dec.returncode == 0
        assert "admin" in dec.stdout
        assert "secret" in dec.stdout

    def test_encrypt_decrypt_key_file(self, tmp_path):
        keygen = self.run_cli("keygen")
        key_file = tmp_path / "key.txt"
        key_file.write_text(keygen.stdout.strip(), encoding="utf-8")
        enc = self.run_cli(
            "encrypt", "-u", "admin", "-p", "secret",
            "--key-file", str(key_file),
        )
        assert enc.returncode == 0
        token = enc.stdout.strip()
        dec = self.run_cli(
            "decrypt", token, "--key-file", str(key_file),
        )
        assert dec.returncode == 0
        assert "admin" in dec.stdout

    def test_encrypt_decrypt_env_key(self):
        keygen = self.run_cli("keygen")
        key = keygen.stdout.strip()
        env = {**os.environ, "CREDENTIALS_KEY": key}
        enc = subprocess.run(
            [sys.executable, "credentials_manager.py",
             "encrypt", "-u", "admin", "-p", "secret"],
            capture_output=True, text=True, env=env,
        )
        assert enc.returncode == 0
        token = enc.stdout.strip()
        dec = subprocess.run(
            [sys.executable, "credentials_manager.py",
             "decrypt", token],
            capture_output=True, text=True, env=env,
        )
        assert dec.returncode == 0
        assert "admin" in dec.stdout

    def test_decrypt_wrong_key_cli(self):
        k1 = self.run_cli("keygen").stdout.strip()
        k2 = self.run_cli("keygen").stdout.strip()
        enc = self.run_cli(
            "encrypt", "-u", "admin", "-p", "secret", f"--key={k1}"
        )
        token = enc.stdout.strip()
        dec = self.run_cli("decrypt", token, f"--key={k2}")
        assert dec.returncode == 1
        assert "Erreur" in dec.stderr

    def test_decrypt_no_key_cli(self):
        result = self.run_cli("decrypt", "sometoken")
        assert result.returncode == 1
        assert "Erreur" in result.stderr

    def test_decrypt_format_json(self):
        key = self.run_cli("keygen").stdout.strip()
        enc = self.run_cli(
            "encrypt", "-u", "admin", "-p", "secret", f"--key={key}"
        )
        token = enc.stdout.strip()
        dec = self.run_cli(
            "decrypt", token, f"--key={key}", "--format", "json"
        )
        assert dec.returncode == 0
        data = json.loads(dec.stdout)
        assert data["username"] == "admin"
        assert data["password"] == "secret"
