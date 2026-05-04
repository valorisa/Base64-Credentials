# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.2.0] - 2026-05-04

### Added

- Mode CLI non-interactif (`encode` / `decode`) pour intégration dans des scripts
- Mode batch avec `-f` pour encoder/décoder depuis un fichier
- Formats de sortie `--format text|json|env`
- Export fichier avec `-o`
- Support des commentaires (`#`) et lignes vides dans les fichiers batch
- Suite de tests complète (52 tests) avec pytest

### Changed

- Compatibilité Python 3.6+ (`typing.Tuple` au lieu de `tuple[str, str]`)
- Meilleure gestion des erreurs de décodage (base64 invalide vs séparateur manquant)
- Renommage des fonctions interactives pour plus de clarté

## [0.1.0] - 2026-05-04

### Added

- Encodage et décodage de credentials en Base64
- Interface interactive avec menu
- Saisie masquée des mots de passe
