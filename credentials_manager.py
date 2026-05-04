#!/usr/bin/env python3
"""Gestionnaire de credentials — encode/décode username:password."""

import argparse
import base64
import binascii
import getpass
import json
import re
import sys
from typing import Dict, List, Tuple

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


def batch_encode(
    input_path: str, encoding: str = DEFAULT_ENCODING
) -> List[Dict[str, str]]:
    """Encode des credentials depuis un fichier ou stdin."""
    results = []
    source = _open_input(input_path)
    try:
        for lineno, line in enumerate(source, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise ValueError(
                    f"Ligne {lineno}: séparateur ':' manquant dans '{line}'"
                )
            username, password = line.split(":", 1)
            encoded = encode_credentials(username, password, encoding)
            results.append({"username": username, "encoded": encoded})
    finally:
        if source is not sys.stdin:
            source.close()
    return results


def batch_decode(
    input_path: str, encoding: str = DEFAULT_ENCODING
) -> List[Dict[str, str]]:
    """Décode des credentials depuis un fichier ou stdin."""
    results = []
    source = _open_input(input_path)
    try:
        for lineno, line in enumerate(source, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                username, password = decode_credentials(line, encoding)
            except ValueError as e:
                raise ValueError(f"Ligne {lineno}: {e}") from e
            results.append({"username": username, "password": password})
    finally:
        if source is not sys.stdin:
            source.close()
    return results


def format_batch_encode(results: List[Dict[str, str]], fmt: str = "text") -> str:
    """Formate les résultats d'un batch encode."""
    if fmt == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    if fmt == "yaml":
        lines = []
        for r in results:
            lines.append(
                f"- username: {_yaml_scalar(r['username'])}\n"
                f"  encoded: {_yaml_scalar(r['encoded'])}"
            )
        return "\n".join(lines)
    lines = []
    for r in results:
        if fmt == "env":
            lines.append(f"# {r['username'] or '(vide)'}")
            lines.append(f"CREDENTIALS={r['encoded']}")
        else:
            lines.append(r["encoded"])
    return "\n".join(lines)


def format_batch_decode(results: List[Dict[str, str]], fmt: str = "text") -> str:
    """Formate les résultats d'un batch decode."""
    if fmt == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    if fmt == "yaml":
        lines = []
        for r in results:
            lines.append(
                f"- username: {_yaml_scalar(r['username'])}\n"
                f"  password: {_yaml_scalar(r['password'])}"
            )
        return "\n".join(lines)
    lines = []
    for r in results:
        if fmt == "env":
            lines.append(f"USERNAME={r['username']}")
            lines.append(f"PASSWORD={r['password']}")
        else:
            lines.append(f"{r['username']}:{r['password']}")
    return "\n".join(lines)


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

    return parser


def main():
    """Point d'entrée principal."""
    parser = build_parser()
    args = parser.parse_args()

    stdin_piped = not sys.stdin.isatty()

    if args.command == "encode":
        enc = args.encoding
        if args.file:
            try:
                results = batch_encode(args.file, enc)
                content = format_batch_encode(results, args.format)
                write_output(content, args.output)
            except (ValueError, FileNotFoundError) as e:
                print(f"Erreur: {e}", file=sys.stderr)
                sys.exit(1)
        elif stdin_piped and not args.password:
            try:
                results = batch_encode("-", enc)
                content = format_batch_encode(results, args.format)
                write_output(content, args.output)
            except ValueError as e:
                print(f"Erreur: {e}", file=sys.stderr)
                sys.exit(1)
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
    elif args.command == "decode":
        enc = args.encoding
        if args.file:
            try:
                results = batch_decode(args.file, enc)
                content = format_batch_decode(results, args.format)
                write_output(content, args.output)
            except (ValueError, FileNotFoundError) as e:
                print(f"Erreur: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.encoded:
            try:
                username, password = decode_credentials(args.encoded, enc)
                content = format_decoded(username, password, args.format)
                write_output(content, args.output)
            except ValueError as e:
                print(f"Erreur: {e}", file=sys.stderr)
                sys.exit(1)
        elif stdin_piped:
            try:
                results = batch_decode("-", enc)
                content = format_batch_decode(results, args.format)
                write_output(content, args.output)
            except ValueError as e:
                print(f"Erreur: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            parser.error("decode nécessite un token, --file, ou stdin")
    else:
        interactive_loop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruption détectée. Au revoir!")
        sys.exit(0)
