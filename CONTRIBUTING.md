# Contribuer à base64-credentials

Merci de votre intérêt pour ce projet ! Les contributions sont les bienvenues.

## Comment contribuer

1. **Fork** le repository
2. **Créez** une branche pour votre fonctionnalité (`git checkout -b feature/ma-feature`)
3. **Codez** votre modification
4. **Testez** — assurez-vous que tous les tests passent :

   ```bash
   python -m pytest test_credentials_manager.py -v
   ```

5. **Committez** avec un message clair
   (`git commit -m 'Add: description courte'`)
6. **Push** vers votre fork (`git push origin feature/ma-feature`)
7. **Ouvrez** une Pull Request

## Conventions

- Code en Python 3.6+ compatible
- Docstrings en français
- Pas de dépendance externe (bibliothèque standard uniquement)
- Chaque nouvelle fonctionnalité doit être accompagnée de tests

## Signaler un bug

Ouvrez une [issue](https://github.com/valorisa/Base64-Credentials/issues) avec :

- La version de Python utilisée
- Les étapes pour reproduire le bug
- Le comportement attendu vs observé

## Proposer une fonctionnalité

Ouvrez une
[issue](https://github.com/valorisa/Base64-Credentials/issues)
décrivant :

- Le cas d'usage
- Le comportement souhaité
- Des exemples d'utilisation
