# Politique de sécurité

## Avertissement important

**Base64 n'est PAS du chiffrement.** Ce projet encode des credentials en Base64
à des fins utilitaires (HTTP Basic Auth, tests, etc.). Il ne fournit aucune
protection cryptographique.

N'utilisez jamais ce projet pour sécuriser des informations sensibles en
production. Préférez des solutions comme HashiCorp Vault, AWS Secrets Manager
ou des bibliothèques de chiffrement (`cryptography`, `PyCryptodome`).

## Signaler une vulnérabilité

Si vous découvrez un problème de sécurité dans ce projet :

1. **Ne créez pas d'issue publique**
2. Contactez le mainteneur via [GitHub](https://github.com/valorisa)
3. Décrivez le problème avec suffisamment de détails pour le reproduire
4. Laissez un délai raisonnable pour la correction avant toute divulgation

## Versions supportées

| Version | Supportée |
|---------|-----------|
| 0.2.x   | Oui       |
| < 0.2   | Non       |
