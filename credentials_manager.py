#!/usr/bin/env python3
import base64
import getpass
import sys


def encode_credentials(username: str, password: str) -> str:
    """Encode les credentials en base64."""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return encoded


def decode_credentials(encoded: str) -> tuple[str, str]:
    """Décode les credentials depuis base64."""
    try:
        decoded = base64.b64decode(encoded.encode()).decode()
        username, password = decoded.split(':', 1)
        return username, password
    except Exception as e:
        raise ValueError("Impossible de décoder les credentials. Données invalides.") from e


def display_menu():
    """Affiche le menu principal."""
    print("\n" + "="*50)
    print("  GESTIONNAIRE DE CREDENTIALS")
    print("="*50)
    print("1. Encoder des credentials")
    print("2. Décoder des credentials")
    print("3. Quitter")
    print("="*50)


def encode_menu():
    """Menu pour encoder des credentials."""
    print("\n--- ENCODAGE DE CREDENTIALS ---")
    username = input("Nom d'utilisateur: ")
    password = getpass.getpass("Mot de passe: ")

    try:
        encoded = encode_credentials(username, password)
        print("\n✓ Credentials encodés avec succès!")
        print(f"\nCredentials encodés (base64):\n{encoded}")
        print("\nConservez cette chaîne de caractères en lieu sûr.")
    except Exception as e:
        print(f"\n✗ Erreur lors de l'encodage: {e}")


def decode_menu():
    """Menu pour décoder des credentials."""
    print("\n--- DÉCODAGE DE CREDENTIALS ---")
    encoded = input("Chaîne encodée (base64): ")

    try:
        username, password = decode_credentials(encoded)
        print("\n✓ Credentials décodés avec succès!")
        print(f"\nNom d'utilisateur: {username}")
        print(f"Mot de passe: {password}")
    except Exception as e:
        print(f"\n✗ Erreur lors du décodage: {e}")


def main():
    """Fonction principale."""
    print("\nBienvenue dans le gestionnaire de credentials (base64)!")

    while True:
        display_menu()
        choice = input("\nVotre choix (1-3): ").strip()

        if choice == '1':
            encode_menu()
        elif choice == '2':
            decode_menu()
        elif choice == '3':
            print("\nAu revoir!")
            sys.exit(0)
        else:
            print("\n✗ Choix invalide. Veuillez choisir 1, 2 ou 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruption détectée. Au revoir!")
        sys.exit(0)
