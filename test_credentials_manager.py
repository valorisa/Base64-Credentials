"""Tests pour credentials_manager."""

import base64
import json
import subprocess
import sys

import pytest

from credentials_manager import (
    batch_decode,
    batch_encode,
    decode_credentials,
    encode_credentials,
    format_batch_decode,
    format_batch_encode,
    format_decoded,
    format_encoded,
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
