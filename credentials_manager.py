#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""Gestionnaire de credentials — encode/décode/chiffre username:password."""

import argparse
import base64
import binascii
import getpass
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_FERNET = True
except ImportError:
    HAS_FERNET = False

try:
    import argcomplete
    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

MENU_WIDTH = 50
MENU_SEPARATOR = "=" * MENU_WIDTH

ENCODINGS = {
    "base64": (
        lambda b: base64.b64encode(b).decode(),
        lambda s: base64.b64decode(s.encode()),
    ),
    "base32": (
        lambda b: base64.b32encode(b).decode(),
        lambda s: base64.b32decode(s.encode()),
    ),
    "hex": (
        lambda b: binascii.hexlify(b).decode(),
        lambda s: binascii.unhexlify(s.encode()),
    ),
    "base85": (
        lambda b: base64.b85encode(b).decode(),
        lambda s: base64.b85decode(s.encode()),
    ),
}

DEFAULT_ENCODING = "base64"

MIN_PASSWORD_LENGTH = 8
PASSWORD_CHECKS = [
    (r"[a-z]", "une minuscule"),
    (r"[A-Z]", "une majuscule"),
    (r"[0-9]", "un chiffre"),
    (r"[^a-zA-Z0-9]", "un caractère spécial"),
]


def check_password_strength(password: str) -> List[str]:
    """Vérifie la force du mot de passe et retourne les avertissements."""
    warnings = []
    if len(password) < MIN_PASSWORD_LENGTH:
        warnings.append(
            f"Longueur insuffisante ({len(password)}/{MIN_PASSWORD_LENGTH})"
        )
    for pattern, label in PASSWORD_CHECKS:
        if not re.search(pattern, password):
            warnings.append(f"Manque {label}")
    return warnings


def encode_credentials(
    username: str, password: str, encoding: str = DEFAULT_ENCODING
) -> str:
    """Encode les credentials avec l'encodage spécifié."""
    credentials = f"{username}:{password}"
    encode_fn, _ = ENCODINGS[encoding]
    return encode_fn(credentials.encode())


def decode_credentials(
    encoded: str, encoding: str = DEFAULT_ENCODING
) -> Tuple[str, str]:
    """Décode les credentials avec l'encodage spécifié."""
    _, decode_fn = ENCODINGS[encoding]
    try:
        decoded = decode_fn(encoded).decode()
    except Exception as e:
        raise ValueError(f"Données {encoding} invalides.") from e

    if ":" not in decoded:
        raise ValueError("Format invalide : séparateur ':' manquant.")

    username, password = decoded.split(":", 1)
    return username, password


def generate_key() -> str:
    """Génère une clé Fernet."""
    if not HAS_FERNET:
        raise RuntimeError(
            "Le module 'cryptography' est requis pour le chiffrement. "
            "Installez-le avec : pip install cryptography"
        )
    return Fernet.generate_key().decode()


def encrypt_credentials(
    username: str, password: str, key: str
) -> str:
    """Chiffre les credentials avec Fernet."""
    if not HAS_FERNET:
        raise RuntimeError(
            "Le module 'cryptography' est requis pour le chiffrement. "
            "Installez-le avec : pip install cryptography"
        )
    credentials = f"{username}:{password}"
    f = Fernet(key.encode())
    return f.encrypt(credentials.encode()).decode()


def decrypt_credentials(token: str, key: str) -> Tuple[str, str]:
    """Déchiffre les credentials avec Fernet."""
    if not HAS_FERNET:
        raise RuntimeError(
            "Le module 'cryptography' est requis pour le chiffrement. "
            "Installez-le avec : pip install cryptography"
        )
    f = Fernet(key.encode())
    try:
        decrypted = f.decrypt(token.encode()).decode()
    except InvalidToken as e:
        raise ValueError(
            "Déchiffrement impossible : clé invalide ou données corrompues."
        ) from e

    if ":" not in decrypted:
        raise ValueError("Format invalide : séparateur ':' manquant.")

    username, password = decrypted.split(":", 1)
    return username, password


def _resolve_key(args) -> str:
    """Résout la clé Fernet depuis les arguments, env, ou fichier."""
    key = getattr(args, "key", None)
    if key:
        return key
    key = os.environ.get("CREDENTIALS_KEY")
    if key:
        return key
    key_file = getattr(args, "key_file", None)
    if key_file:
        with open(key_file, "r", encoding="utf-8") as kf:
            return kf.read().strip()
    raise ValueError(
        "Clé requise : --key, --key-file, ou variable CREDENTIALS_KEY"
    )


def _yaml_scalar(value: str) -> str:
    """Échappe une valeur pour YAML si nécessaire."""
    if not value or re.search(r"[:{}\[\],&*?|>!%@`\n#]", value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def format_encoded(encoded: str, fmt: str = "text") -> str:
    """Formate un résultat d'encodage selon le format demandé."""
    if fmt == "json":
        return json.dumps({"encoded": encoded})
    if fmt == "env":
        return f"CREDENTIALS={encoded}"
    if fmt == "yaml":
        return f"encoded: {_yaml_scalar(encoded)}"
    return encoded


def format_decoded(username: str, password: str, fmt: str = "text") -> str:
    """Formate un résultat de décodage selon le format demandé."""
    if fmt == "json":
        return json.dumps({"username": username, "password": password})
    if fmt == "env":
        return f"USERNAME={username}\nPASSWORD={password}"
    if fmt == "yaml":
        return (
            f"username: {_yaml_scalar(username)}\n"
            f"password: {_yaml_scalar(password)}"
        )
    return f"Nom d'utilisateur: {username}\nMot de passe: {password}"


def write_output(content: str, output_path: str = None):
    """Écrit le contenu sur stdout ou dans un fichier."""
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
    else:
        print(content)


def _open_input(input_path: str):
    """Ouvre un fichier ou stdin si input_path vaut '-'."""
    if input_path == "-":
        return sys.stdin
    return open(input_path, "r", encoding="utf-8")


def _batch_process(input_path: str, line_processor) -> List[Dict[str, str]]:
    """Traite un fichier ligne par ligne, en ignorant commentaires et blancs."""
    results = []
    source = _open_input(input_path)
    try:
        for lineno, line in enumerate(source, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            results.append(line_processor(lineno, line))
    finally:
        if source is not sys.stdin:
            source.close()
    return results


def batch_encode(
    input_path: str, encoding: str = DEFAULT_ENCODING
) -> List[Dict[str, str]]:
    """Encode des credentials depuis un fichier ou stdin."""
    def process_line(lineno, line):
        if ":" not in line:
            raise ValueError(
                f"Ligne {lineno}: séparateur ':' manquant dans '{line}'"
            )
        username, password = line.split(":", 1)
        encoded = encode_credentials(username, password, encoding)
        return {"username": username, "encoded": encoded}
    return _batch_process(input_path, process_line)


def batch_decode(
    input_path: str, encoding: str = DEFAULT_ENCODING
) -> List[Dict[str, str]]:
    """Décode des credentials depuis un fichier ou stdin."""
    def process_line(lineno, line):
        try:
            username, password = decode_credentials(line, encoding)
        except ValueError as e:
            raise ValueError(f"Ligne {lineno}: {e}") from e
        return {"username": username, "password": password}
    return _batch_process(input_path, process_line)


def _format_batch(results, fmt, yaml_item, env_item, text_item) -> str:
    """Formate une liste de résultats batch selon le format demandé."""
    if fmt == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    lines = []
    for r in results:
        if fmt == "yaml":
            lines.append(yaml_item(r))
        elif fmt == "env":
            lines.extend(env_item(r))
        else:
            lines.append(text_item(r))
    return "\n".join(lines)


def format_batch_encode(results: List[Dict[str, str]], fmt: str = "text") -> str:
    """Formate les résultats d'un batch encode."""
    return _format_batch(
        results, fmt,
        yaml_item=lambda r: (
            f"- username: {_yaml_scalar(r['username'])}\n"
            f"  encoded: {_yaml_scalar(r['encoded'])}"
        ),
        env_item=lambda r: [
            f"# {r['username'] or '(vide)'}",
            f"CREDENTIALS={r['encoded']}",
        ],
        text_item=lambda r: r["encoded"],
    )


def format_batch_decode(results: List[Dict[str, str]], fmt: str = "text") -> str:
    """Formate les résultats d'un batch decode."""
    return _format_batch(
        results, fmt,
        yaml_item=lambda r: (
            f"- username: {_yaml_scalar(r['username'])}\n"
            f"  password: {_yaml_scalar(r['password'])}"
        ),
        env_item=lambda r: [
            f"USERNAME={r['username']}",
            f"PASSWORD={r['password']}",
        ],
        text_item=lambda r: f"{r['username']}:{r['password']}",
    )


def display_menu():
    """Affiche le menu principal."""
    print(f"\n{MENU_SEPARATOR}")
    print("  GESTIONNAIRE DE CREDENTIALS")
    print(MENU_SEPARATOR)
    print("1. Encoder des credentials")
    print("2. Décoder des credentials")
    print("3. Quitter")
    print(MENU_SEPARATOR)


def encode_interactive():
    """Flow interactif pour encoder des credentials."""
    print("\n--- ENCODAGE DE CREDENTIALS ---")
    username = input("Nom d'utilisateur: ")
    password = getpass.getpass("Mot de passe: ")
    encoded = encode_credentials(username, password)
    print("\n✓ Credentials encodés avec succès!")
    print(f"\nCredentials encodés (base64):\n{encoded}")
    print("\nConservez cette chaîne de caractères en lieu sûr.")


def decode_interactive():
    """Flow interactif pour décoder des credentials."""
    print("\n--- DÉCODAGE DE CREDENTIALS ---")
    encoded = input("Chaîne encodée (base64): ")
    username, password = decode_credentials(encoded)
    print("\n✓ Credentials décodés avec succès!")
    print(f"\nNom d'utilisateur: {username}")
    print(f"Mot de passe: {password}")


def interactive_loop():
    """Boucle interactive principale."""
    print("\nBienvenue dans le gestionnaire de credentials (base64)!")

    handlers = {"1": encode_interactive, "2": decode_interactive}

    while True:
        display_menu()
        choice = input("\nVotre choix (1-3): ").strip()

        if choice == "3":
            print("\nAu revoir!")
            sys.exit(0)

        handler = handlers.get(choice)
        if handler is None:
            print("\n✗ Choix invalide. Veuillez choisir 1, 2 ou 3.")
            continue

        try:
            handler()
        except ValueError as e:
            print(f"\n✗ Erreur: {e}")


def _add_common_args(parser: argparse.ArgumentParser):
    """Ajoute les arguments communs à un sous-parser."""
    parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="Écrire le résultat dans un fichier",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "env", "yaml"],
        default="text",
        help="Format de sortie (défaut: text)",
    )
    parser.add_argument(
        "--encoding",
        choices=list(ENCODINGS.keys()),
        default=DEFAULT_ENCODING,
        help=f"Encodage à utiliser (défaut: {DEFAULT_ENCODING})",
    )


def build_parser() -> argparse.ArgumentParser:
    """Construit le parser d'arguments CLI."""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de credentials Base64"
    )
    subparsers = parser.add_subparsers(dest="command")

    encode_parser = subparsers.add_parser("encode", help="Encoder des credentials")
    encode_parser.add_argument("-u", "--username", default="", help="Nom d'utilisateur")
    encode_parser.add_argument(
        "-p", "--password",
        help="Mot de passe (déconseillé en CLI, préférer la saisie interactive)",
    )
    encode_parser.add_argument(
        "-f", "--file", metavar="FILE",
        help="Mode batch : fichier avec un username:password par ligne",
    )
    encode_parser.add_argument(
        "--check-password", action="store_true",
        help="Vérifier la force du mot de passe",
    )
    _add_common_args(encode_parser)

    decode_parser = subparsers.add_parser("decode", help="Décoder des credentials")
    decode_parser.add_argument("encoded", nargs="?", help="Chaîne encodée à décoder")
    decode_parser.add_argument(
        "-f", "--file", metavar="FILE",
        help="Mode batch : fichier avec un token encodé par ligne",
    )
    _add_common_args(decode_parser)

    keygen_parser = subparsers.add_parser(
        "keygen", help="Générer une clé de chiffrement Fernet"
    )
    keygen_parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="Écrire la clé dans un fichier",
    )

    encrypt_parser = subparsers.add_parser(
        "encrypt", help="Chiffrer des credentials avec Fernet"
    )
    encrypt_parser.add_argument(
        "-u", "--username", default="", help="Nom d'utilisateur",
    )
    encrypt_parser.add_argument(
        "-p", "--password",
        help="Mot de passe",
    )
    encrypt_parser.add_argument(
        "--key", help="Clé Fernet (ou via CREDENTIALS_KEY)",
    )
    encrypt_parser.add_argument(
        "--key-file", metavar="FILE",
        help="Fichier contenant la clé Fernet",
    )
    encrypt_parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="Écrire le résultat dans un fichier",
    )

    decrypt_parser = subparsers.add_parser(
        "decrypt", help="Déchiffrer des credentials avec Fernet"
    )
    decrypt_parser.add_argument("token", help="Token chiffré Fernet")
    decrypt_parser.add_argument(
        "--key", help="Clé Fernet (ou via CREDENTIALS_KEY)",
    )
    decrypt_parser.add_argument(
        "--key-file", metavar="FILE",
        help="Fichier contenant la clé Fernet",
    )
    decrypt_parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="Écrire le résultat dans un fichier",
    )
    decrypt_parser.add_argument(
        "--format",
        choices=["text", "json", "env", "yaml"],
        default="text",
        help="Format de sortie (défaut: text)",
    )

    return parser


def _handle_encode(args, parser, stdin_piped):
    """Gère la commande encode."""
    enc = args.encoding
    if args.file:
        results = batch_encode(args.file, enc)
        content = format_batch_encode(results, args.format)
        write_output(content, args.output)
    elif stdin_piped and not args.password:
        results = batch_encode("-", enc)
        content = format_batch_encode(results, args.format)
        write_output(content, args.output)
    else:
        password = args.password or getpass.getpass("Mot de passe: ")
        if args.check_password:
            warnings = check_password_strength(password)
            if warnings:
                for w in warnings:
                    print(f"⚠ {w}", file=sys.stderr)
        encoded = encode_credentials(args.username, password, enc)
        content = format_encoded(encoded, args.format)
        write_output(content, args.output)


def _handle_decode(args, parser, stdin_piped):
    """Gère la commande decode."""
    enc = args.encoding
    if args.file:
        results = batch_decode(args.file, enc)
        content = format_batch_decode(results, args.format)
        write_output(content, args.output)
    elif args.encoded:
        username, password = decode_credentials(args.encoded, enc)
        content = format_decoded(username, password, args.format)
        write_output(content, args.output)
    elif stdin_piped:
        results = batch_decode("-", enc)
        content = format_batch_decode(results, args.format)
        write_output(content, args.output)
    else:
        parser.error("decode nécessite un token, --file, ou stdin")


def _handle_keygen(args, parser, stdin_piped):
    """Gère la commande keygen."""
    key = generate_key()
    write_output(key, args.output)


def _handle_encrypt(args, parser, stdin_piped):
    """Gère la commande encrypt."""
    key = _resolve_key(args)
    password = args.password or getpass.getpass("Mot de passe: ")
    token = encrypt_credentials(args.username, password, key)
    write_output(token, args.output)


def _handle_decrypt(args, parser, stdin_piped):
    """Gère la commande decrypt."""
    key = _resolve_key(args)
    username, password = decrypt_credentials(args.token, key)
    content = format_decoded(username, password, args.format)
    write_output(content, args.output)


_COMMAND_HANDLERS = {
    "encode": _handle_encode,
    "decode": _handle_decode,
    "keygen": _handle_keygen,
    "encrypt": _handle_encrypt,
    "decrypt": _handle_decrypt,
}


def main():
    """Point d'entrée principal."""
    parser = build_parser()
    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)
    args = parser.parse_args()

    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        interactive_loop()
        return

    stdin_piped = not sys.stdin.isatty()
    try:
        handler(args, parser, stdin_piped)
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruption détectée. Au revoir!")
        sys.exit(0)
