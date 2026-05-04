# base64-credentials

[![CI](https://github.com/valorisa/Base64-Credentials/actions/workflows/ci.yml/badge.svg)](https://github.com/valorisa/Base64-Credentials/actions/workflows/ci.yml)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 109](https://img.shields.io/badge/tests-109%20passed-brightgreen.svg)](test_credentials_manager.py)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

Un outil CLI Python complet pour **encoder**, **décoder** et **chiffrer** des credentials (`username:password`),
conçu pour les développeurs, les administrateurs systèmes et les équipes DevOps qui manipulent quotidiennement
des identifiants dans leurs workflows d'automatisation.

## Table des matières

- [Description](#description)
- [Pourquoi ce projet ?](#pourquoi-ce-projet-)
- [Aperçu rapide](#aperçu-rapide)
- [Avertissement de sécurité](#avertissement-de-sécurité)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Exemples](#exemples)
- [Comment ça fonctionne](#comment-ça-fonctionne)
- [Cas d'usage](#cas-dusage)
- [Limitations](#limitations)
- [Contribution](#contribution)
- [Licence](#licence)
- [Auteur](#auteur)

## Description

**base64-credentials** est un utilitaire en ligne de commande écrit en Python qui permet d'encoder, de décoder
et de **chiffrer** des identifiants (username et password) en utilisant plusieurs formats d'encodage (Base64,
Base32, Hex, Base85) ainsi que le chiffrement symétrique Fernet pour une protection cryptographique réelle.

L'outil offre trois modes d'utilisation :

- **Mode interactif** : un menu guidé pour les opérations ponctuelles, avec saisie masquée du mot de passe
- **Mode CLI** : des commandes non-interactives (`encode`, `decode`, `encrypt`, `decrypt`, `keygen`) pour
  l'intégration dans des scripts, pipelines CI/CD et workflows d'automatisation
- **Mode stdin/pipe** : lecture automatique depuis l'entrée standard, permettant le chaînage avec d'autres
  commandes Unix

Les résultats peuvent être exportés en **5 formats** (text, JSON, YAML, env, fichier) et le **mode batch**
permet de traiter des centaines de credentials en une seule commande.

Le projet a été conçu avec une philosophie **zéro dépendance requise** : toutes les fonctionnalités
d'encodage/décodage reposent sur la bibliothèque standard Python. Les fonctionnalités avancées (chiffrement
Fernet, autocomplétion shell) sont disponibles via des dépendances optionnelles installables à la demande.

## Pourquoi ce projet ?

La manipulation de credentials est une tâche récurrente pour tout développeur ou administrateur système :

- **Tester une API** protégée par HTTP Basic Authentication ? Il faut encoder `admin:password` en Base64 pour
  le header `Authorization`.
- **Stocker des identifiants** dans un fichier de configuration ? On souhaite les rendre non-lisibles à l'œil
  nu sans pour autant déployer une solution de gestion de secrets.
- **Migrer des credentials** entre environnements ? Le mode batch encode ou décode des centaines d'identifiants
  en une commande.
- **Sécuriser réellement** des identifiants sensibles ? Le chiffrement Fernet offre une protection
  cryptographique symétrique que le simple encodage Base64 ne fournit pas.

**base64-credentials** rassemble toutes ces opérations dans un seul outil léger, sans installation complexe,
utilisable aussi bien à la main qu'intégré dans un pipeline automatisé.

## Aperçu rapide

```bash
# Encoder des credentials
credentials-manager encode -u admin -p secret
# YWRtaW46c2VjcmV0

# Décoder
credentials-manager decode YWRtaW46c2VjcmV0
# Nom d'utilisateur: admin
# Mot de passe: secret

# Chiffrer avec Fernet (protection réelle)
credentials-manager keygen > key.txt
credentials-manager encrypt -u admin -p secret --key-file key.txt
# gAAAAABp...

# Mode pipe
echo "admin:secret" | credentials-manager encode
echo "admin:secret" | credentials-manager encode | credentials-manager decode

# Mode batch + JSON
credentials-manager encode -f creds.txt --format json
```

## Avertissement de sécurité

> **IMPORTANT : Base64 n'est PAS du chiffrement !**
>
> L'encodage Base64 (ainsi que Base32, Hex et Base85) est **facilement réversible** par n'importe qui.
> Il ne fournit **aucune sécurité cryptographique**. Ne l'utilisez jamais seul pour protéger des informations
> sensibles en production.
>
> Ces encodages servent uniquement à :
>
> - Rendre du texte non-lisible à première vue
> - Encoder des données binaires en ASCII
> - Respecter des formats qui nécessitent du texte (comme les headers HTTP)
>
> **Pour une protection réelle**, utilisez la commande `encrypt` de cet outil (chiffrement Fernet/AES-128-CBC),
> ou des solutions dédiées comme HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, etc.

## Fonctionnalités

- ✅ **Encodages multiples** : base64, base32, hex, base85
- ✅ **Décodage** : Récupère les credentials depuis une chaîne encodée
- ✅ **Interface interactive** : Menu simple et intuitif
- ✅ **Saisie masquée** : Les mots de passe ne s'affichent pas à l'écran lors de la saisie
- ✅ **Username optionnel** : Possibilité d'encoder uniquement un mot de passe
- ✅ **Gestion des erreurs** : Messages clairs en cas de données invalides
- ✅ **Chiffrement Fernet** : `encrypt`/`decrypt` avec clé symétrique
- ✅ **Autocomplétion shell** : bash/zsh/fish via argcomplete
- ✅ **Docker** : Image minimale disponible
- ✅ **Man page** : `credentials-manager.1` incluse
- ✅ **Aucune dépendance requise** : stdlib uniquement (crypto et completion optionnels)
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

Téléchargez le fichier `credentials_manager.py` directement depuis GitHub et placez-le dans un dossier de
votre choix.

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
python3 credentials_manager.py encode -u admin -p secret --encoding base32
# MFSG22LOHJZWKY3SMV2A====

python3 credentials_manager.py encode -u admin -p secret --encoding hex
# 61646d696e3a736563726574

python3 credentials_manager.py decode MFSG22LOHJZWKY3SMV2A==== --encoding base32
# Nom d'utilisateur: admin
# Mot de passe: secret
```

Chiffrement Fernet (nécessite `pip install cryptography`) :

```bash
# Générer une clé
python3 credentials_manager.py keygen > key.txt

# Chiffrer
python3 credentials_manager.py encrypt -u admin -p secret --key-file key.txt
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
register-python-argcomplete --shell fish credentials-manager | source
```

Validation de la force du mot de passe :

```bash
python3 credentials_manager.py encode -u admin -p ab --check-password
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

Mode batch (`-f`) — un élément par ligne, les lignes vides et `#` commentaires sont ignorés :

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
echo "admin:secret" | python3 credentials_manager.py encode | python3 credentials_manager.py decode
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

Stockez des credentials dans des fichiers de configuration de manière non-lisible à l'œil nu
(mais toujours non-sécurisée) :

```ini
[database]
credentials=dXNlcjpwYXNzd29yZA==
```

## Limitations

- ❌ **Pas de sécurité** : Base64 est facilement décodable
- ❌ **Format fixe** : Le format `username:password` est imposé
- ❌ **Pas de validation** : Aucune vérification des credentials
- ❌ **Pas de stockage** : Les credentials ne sont pas sauvegardés
- ❌ **Sensible aux caractères spéciaux** : Les `:` dans les passwords peuvent poser problème

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
- Repository : [https://github.com/valorisa/Base64-Credentials](https://github.com/valorisa/Base64-Credentials)

---

Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !
