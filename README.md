# base64-credentials

[![CI](https://github.com/valorisa/Base64-Credentials/actions/workflows/ci.yml/badge.svg)](https://github.com/valorisa/Base64-Credentials/actions/workflows/ci.yml)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un gestionnaire de credentials simple et interactif utilisant l'encodage Base64.

## Table des matières

- [Description](#description)
- [Avertissement de sécurité](#avertissement-de-sécurité)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
  - [Lancement du script](#lancement-du-script)
  - [Option 1 : Encoder des credentials](#option-1--encoder-des-credentials)
  - [Option 2 : Décoder des credentials](#option-2--décoder-des-credentials)
  - [Option 3 : Quitter](#option-3--quitter)
- [Exemples](#exemples)
  - [Exemple d'encodage avec username et password](#exemple-dencodage-avec-username-et-password)
  - [Exemple d'encodage avec password uniquement](#exemple-dencodage-avec-password-uniquement)
  - [Exemple de décodage](#exemple-de-décodage)
- [Comment ça fonctionne](#comment-ça-fonctionne)
  - [Processus d'encodage](#processus-dencodage)
  - [Processus de décodage](#processus-de-décodage)
- [Cas d'usage](#cas-dusage)
- [Limitations](#limitations)
- [Contribution](#contribution)
- [Licence](#licence)
- [Auteur](#auteur)

## Description

**base64-credentials** est un utilitaire en ligne de commande écrit en Python
qui permet d'encoder et de décoder facilement des identifiants (username et
password) en utilisant l'encodage Base64. Il offre à la fois un mode interactif
avec menu et un mode CLI non-interactif pour l'intégration dans des scripts
et pipelines.

Ce projet est idéal pour :

- Encoder rapidement des credentials pour des tests
- Stocker des identifiants de manière non-lisible à l'œil nu
- Passer des credentials dans des URLs ou headers HTTP
- Automatiser l'encodage/décodage de credentials en Basic Authentication

## Avertissement de sécurité

> **⚠️ IMPORTANT : Base64 n'est PAS du chiffrement !**
>
> L'encodage Base64 est facilement réversible par n'importe qui.
> Il ne fournit **AUCUNE sécurité cryptographique**. Ne l'utilisez jamais
> pour protéger des informations sensibles en production.
>
> Base64 sert uniquement à :
>
> - Rendre du texte non-lisible à première vue
> - Encoder des données binaires en ASCII
> - Respecter des formats qui nécessitent du texte (comme les headers HTTP)
>
> Pour un chiffrement réel, utilisez des bibliothèques comme `cryptography`,
> `PyCryptodome`, ou des solutions de gestion de secrets comme
> HashiCorp Vault, AWS Secrets Manager, etc.

## Fonctionnalités

- ✅ **Encodages multiples** : base64, base32, hex, base85
- ✅ **Décodage** : Récupère les credentials depuis une chaîne encodée
- ✅ **Interface interactive** : Menu simple et intuitif
- ✅ **Saisie masquée** : Les mots de passe ne s'affichent pas à l'écran
  lors de la saisie
- ✅ **Username optionnel** : Possibilité d'encoder uniquement un mot de passe
- ✅ **Gestion des erreurs** : Messages clairs en cas de données
  invalides
- ✅ **Chiffrement Fernet** : `encrypt`/`decrypt` avec clé symétrique
- ✅ **Autocomplétion shell** : bash/zsh/fish via argcomplete
- ✅ **Docker** : Image minimale disponible
- ✅ **Man page** : `credentials-manager.1` incluse
- ✅ **Aucune dépendance requise** : stdlib uniquement (crypto et
  completion optionnels)
- ✅ **Mode CLI** : Utilisation non-interactive pour les scripts et pipelines
- ✅ **Support stdin** : Lecture depuis pipe (`echo "user:pass" | ... encode`)
- ✅ **Mode batch** : Encodage/décodage en masse depuis un fichier
- ✅ **Formats de sortie** : text, JSON, env, YAML
- ✅ **Validation mot de passe** : `--check-password` optionnel
- ✅ **Export fichier** : Option `-o` pour écrire le résultat dans un fichier
- ✅ **Compatible** : Fonctionne avec Python 3.6+

## Prérequis

- Python 3.6 ou supérieur
- `cryptography` (optionnel, pour encrypt/decrypt)
- `argcomplete` (optionnel, pour l'autocomplétion shell)

Vérifiez votre version de Python :

```bash
python3 --version
```

## Installation

### Méthode 1 : pip (recommandé)

```bash
pip install base64-credentials
pip install base64-credentials[all]  # avec crypto + completion
```

### Méthode 2 : Clonage du repository

```bash
git clone https://github.com/valorisa/Base64-Credentials.git
cd Base64-Credentials
```

### Méthode 3 : Docker

```bash
docker build -t credentials-manager .
docker run --rm credentials-manager encode -u admin -p secret
```

### Méthode 4 : Téléchargement direct

Téléchargez le fichier `credentials_manager.py` directement
depuis GitHub.

### Rendre le script exécutable (optionnel)

Sur Linux/macOS :

```bash
chmod +x credentials_manager.py
```

## Utilisation

### Lancement du script

Depuis le dossier contenant le script :

```bash
python3 credentials_manager.py
```

Ou si vous l'avez rendu exécutable :

```bash
./credentials_manager.py
```

### Mode CLI (non-interactif)

Encoder des credentials directement :

```bash
python3 credentials_manager.py encode -u admin
# Le mot de passe est demandé de manière masquée

python3 credentials_manager.py encode -u admin -p secret123
# Résultat : YWRtaW46c2VjcmV0MTIz
```

Encodages alternatifs (`--encoding`) :

```bash
python3 credentials_manager.py encode -u admin -p secret \
  --encoding base32
# MFSG22LOHJZWKY3SMV2A====

python3 credentials_manager.py encode -u admin -p secret \
  --encoding hex
# 61646d696e3a736563726574

python3 credentials_manager.py decode MFSG22LOHJZWKY3SMV2A==== \
  --encoding base32
# Nom d'utilisateur: admin
# Mot de passe: secret
```

Chiffrement Fernet (nécessite `pip install cryptography`) :

```bash
# Générer une clé
python3 credentials_manager.py keygen > key.txt

# Chiffrer
python3 credentials_manager.py encrypt -u admin -p secret \
  --key-file key.txt
# gAAAAABp...

# Déchiffrer
python3 credentials_manager.py decrypt TOKEN --key-file key.txt
# Nom d'utilisateur: admin
# Mot de passe: secret

# Via variable d'environnement
export CREDENTIALS_KEY=$(cat key.txt)
python3 credentials_manager.py encrypt -u admin -p secret
python3 credentials_manager.py decrypt TOKEN --format json
```

Autocomplétion shell (nécessite `pip install argcomplete`) :

```bash
# bash
eval "$(register-python-argcomplete credentials-manager)"

# zsh
eval "$(register-python-argcomplete credentials-manager)"

# fish
register-python-argcomplete --shell fish \
  credentials-manager | source
```

Validation de la force du mot de passe :

```bash
python3 credentials_manager.py encode -u admin -p ab \
  --check-password
# ⚠ Longueur insuffisante (2/8)
# ⚠ Manque une majuscule
# ⚠ Manque un chiffre
# ⚠ Manque un caractère spécial
# YWRtaW46YWI=
```

Décoder des credentials :

```bash
python3 credentials_manager.py decode YWRtaW46c2VjcmV0MTIz
# Nom d'utilisateur: admin
# Mot de passe: secret123
```

Formats de sortie (`--format`) :

```bash
# JSON
python3 credentials_manager.py encode -u admin -p secret --format json
# {"encoded": "YWRtaW46c2VjcmV0"}

python3 credentials_manager.py decode YWRtaW46c2VjcmV0 --format json
# {"username": "admin", "password": "secret"}

# Variables d'environnement
python3 credentials_manager.py encode -u admin -p secret --format env
# CREDENTIALS=YWRtaW46c2VjcmV0

python3 credentials_manager.py decode YWRtaW46c2VjcmV0 --format env
# USERNAME=admin
# PASSWORD=secret
```

Export dans un fichier (`-o`) :

```bash
python3 credentials_manager.py encode -u admin -p secret -o token.txt
python3 credentials_manager.py decode YWRtaW46c2VjcmV0 -o creds.env --format env
```

Mode batch (`-f`) — un élément par ligne,
les lignes vides et `#` commentaires sont ignorés :

```bash
# Fichier d'entrée (creds.txt) :
# admin:secret123
# user2:password2

python3 credentials_manager.py encode -f creds.txt
# YWRtaW46c2VjcmV0MTIz
# dXNlcjI6cGFzc3dvcmQy

python3 credentials_manager.py encode -f creds.txt --format json
# [{"username": "admin", "encoded": "YWRtaW46c2VjcmV0MTIz"}, ...]

python3 credentials_manager.py encode -f creds.txt --format json -o tokens.json
```

```bash
# Fichier de tokens (tokens.txt) :
# YWRtaW46c2VjcmV0MTIz
# dXNlcjI6cGFzc3dvcmQy

python3 credentials_manager.py decode -f tokens.txt
# admin:secret123
# user2:password2

python3 credentials_manager.py decode -f tokens.txt --format json
# [{"username": "admin", "password": "secret123"}, ...]
```

Lecture depuis stdin (pipe) — détecté automatiquement :

```bash
echo "admin:secret" | python3 credentials_manager.py encode
# YWRtaW46c2VjcmV0

echo "YWRtaW46c2VjcmV0" | python3 credentials_manager.py decode
# admin:secret

# Chaînage complet :
echo "admin:secret" | python3 credentials_manager.py encode \
  | python3 credentials_manager.py decode
# admin:secret

# Batch via stdin :
cat creds.txt | python3 credentials_manager.py encode --format json
```

Utilisation dans un pipeline :

```bash
TOKEN=$(python3 credentials_manager.py encode -u admin -p secret123)
curl -H "Authorization: Basic $TOKEN" https://api.example.com/data
```

### Mode interactif

Sans argument, le script lance le menu interactif :

```bash
python3 credentials_manager.py
```

### Option 1 : Encoder des credentials

1. Sélectionnez `1` dans le menu
2. Entrez votre nom d'utilisateur (ou laissez vide et appuyez sur Entrée)
3. Entrez votre mot de passe (la saisie est masquée)
4. Le script affiche la chaîne encodée en Base64

### Option 2 : Décoder des credentials

1. Sélectionnez `2` dans le menu
2. Collez ou tapez la chaîne Base64 encodée
3. Le script affiche le username et le password décodés

### Option 3 : Quitter

Sélectionnez `3` pour quitter le programme, ou appuyez sur `Ctrl+C` à tout moment.

## Exemples

### Exemple d'encodage avec username et password

```text
==================================================
  GESTIONNAIRE DE CREDENTIALS
==================================================
1. Encoder des credentials
2. Décoder des credentials
3. Quitter
==================================================

Votre choix (1-3): 1

--- ENCODAGE DE CREDENTIALS ---
Nom d'utilisateur: admin
Mot de passe: 

✓ Credentials encodés avec succès!

Credentials encodés (base64):
YWRtaW46c2VjcmV0MTIz

Conservez cette chaîne de caractères en lieu sûr.
```

### Exemple d'encodage avec password uniquement

```text
Votre choix (1-3): 1

--- ENCODAGE DE CREDENTIALS ---
Nom d'utilisateur: 
Mot de passe: 

✓ Credentials encodés avec succès!

Credentials encodés (base64):
Om1vbm1vdGRlcGFzc2U=

Conservez cette chaîne de caractères en lieu sûr.
```

### Exemple de décodage

```text
Votre choix (1-3): 2

--- DÉCODAGE DE CREDENTIALS ---
Chaîne encodée (base64): YWRtaW46c2VjcmV0MTIz

✓ Credentials décodés avec succès!

Nom d'utilisateur: admin
Mot de passe: secret123
```

## Comment ça fonctionne

### Processus d'encodage

1. **Concaténation** : Le script combine username et password avec `:` comme séparateur
   - Exemple : `admin:secret123`

2. **Conversion en bytes** : La chaîne est convertie en bytes UTF-8
   - `"admin:secret123"` → `b'admin:secret123'`

3. **Encodage Base64** : Les bytes sont encodés en Base64
   - `b'admin:secret123'` → `b'YWRtaW46c2VjcmV0MTIz'`

4. **Conversion en string** : Le résultat Base64 est converti en string
   - Résultat : `YWRtaW46c2VjcmV0MTIz`

### Processus de décodage

1. **Conversion en bytes** : La chaîne Base64 est convertie en bytes
   - `"YWRtaW46c2VjcmV0MTIz"` → `b'YWRtaW46c2VjcmV0MTIz'`

2. **Décodage Base64** : Les bytes Base64 sont décodés
   - `b'YWRtaW46c2VjcmV0MTIz'` → `b'admin:secret123'`

3. **Conversion en string** : Les bytes décodés sont convertis en string
   - `b'admin:secret123'` → `"admin:secret123"`

4. **Séparation** : La chaîne est divisée au premier `:`
   - Résultat : `username = "admin"`, `password = "secret123"`

## Cas d'usage

### HTTP Basic Authentication

Générez facilement des headers d'authentification Basic :

```bash
# Encodez vos credentials
python3 credentials_manager.py
# Entrez: admin / password123
# Résultat: YWRtaW46cGFzc3dvcmQxMjM=

# Utilisez dans un header HTTP
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

### Tests API

Encodez rapidement des credentials pour tester des endpoints protégés :

```bash
curl -H "Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=" https://api.example.com/data
```

### Scripts automatisés

Décodez des credentials stockés en Base64 dans vos scripts :

```python
import base64

encoded = "YWRtaW46cGFzc3dvcmQxMjM="
decoded = base64.b64decode(encoded).decode()
username, password = decoded.split(':', 1)
```

### Configuration non-lisible

Stockez des credentials dans des fichiers de configuration de manière
non-lisible à l'œil nu (mais toujours non-sécurisée) :

```ini
[database]
credentials=dXNlcjpwYXNzd29yZA==
```

## Limitations

- ❌ **Pas de sécurité** : Base64 est facilement décodable
- ❌ **Format fixe** : Le format `username:password` est imposé
- ❌ **Pas de validation** : Aucune vérification des credentials
- ❌ **Pas de stockage** : Les credentials ne sont pas sauvegardés
- ❌ **Sensible aux caractères spéciaux** : Les `:` dans les passwords
  peuvent poser problème

## Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le projet
2. **Créez** une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. **Committez** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. **Ouvrez** une Pull Request

### Idées de fonctionnalités futures

- Interface graphique (GUI)
- Batch encrypt/decrypt
- Rotation de clé Fernet

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Auteur

### valorisa

- GitHub : [@valorisa](https://github.com/valorisa)
- Repository :
  [https://github.com/valorisa/b64-credentials](https://github.com/valorisa/b64-credentials)

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile
sur GitHub !
