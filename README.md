# base64-credentials

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

**b64-credentials** est un utilitaire en ligne de commande écrit en Python
qui permet d'encoder et de décoder facilement des identifiants (username et
password) en utilisant l'encodage Base64. Le script offre une interface
interactive avec un menu simple pour effectuer ces opérations de manière
réversible.

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

- ✅ **Encodage Base64** : Transforme username:password en chaîne Base64
- ✅ **Décodage Base64** : Récupère les credentials depuis une chaîne encodée
- ✅ **Interface interactive** : Menu simple et intuitif
- ✅ **Saisie masquée** : Les mots de passe ne s'affichent pas à l'écran
  lors de la saisie
- ✅ **Username optionnel** : Possibilité d'encoder uniquement un mot de passe
- ✅ **Gestion des erreurs** : Messages clairs en cas de données
  invalides
- ✅ **Aucune dépendance externe** : Utilise uniquement la bibliothèque
  standard Python
- ✅ **Compatible** : Fonctionne avec Python 3.6+

## Prérequis

- Python 3.6 ou supérieur

Vérifiez votre version de Python :

```bash
python3 --version
```

## Installation

### Méthode 1 : Clonage du repository

```bash
git clone https://github.com/valorisa/b64-credentials.git
cd b64-credentials
```

### Méthode 2 : Téléchargement direct

Téléchargez le fichier `credentials_manager.py` directement depuis GitHub
et placez-le dans un dossier de votre choix.

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

- Support de différents formats d'encodage (hex, base32, etc.)
- Mode batch pour encoder/décoder plusieurs credentials
- Export vers fichier
- Support d'autres formats (JSON, YAML)
- Interface graphique (GUI)
- Option de chiffrement réel (AES, Fernet)

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
