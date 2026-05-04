# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.4.0] - 2026-05-04

### Added (0.4.0)

- Encodages alternatifs : `--encoding base32|hex|base85`
- Validation de mot de passe : `--check-password`
- Format de sortie YAML : `--format yaml`
- 33 nouveaux tests (93 tests au total)
- Corrections markdownlint (0 violation)

## [0.3.0] - 2026-05-04

### Added (0.3.0)

- Support stdin/pipe : `echo "admin:secret" | ... encode`
- Chaînage pipe complet : `encode | decode` roundtrip
- Badges CI, Python, License dans le README
- 8 nouveaux tests stdin (60 tests au total)

## [0.2.0] - 2026-05-04

### Added (0.2.0)

- Mode CLI non-interactif (`encode` / `decode`)
- Mode batch avec `-f` pour encoder/décoder depuis un fichier
- Formats de sortie `--format text|json|env`
- Export fichier avec `-o`
- Support des commentaires (`#`) et lignes vides en batch
- Suite de tests complète (52 tests) avec pytest

### Changed

- Compatibilité Python 3.6+ (`typing.Tuple`)
- Meilleure gestion des erreurs de décodage
- Renommage des fonctions interactives

## [0.1.0] - 2026-05-04

### Added (0.1.0)

- Encodage et décodage de credentials en Base64
- Interface interactive avec menu
- Saisie masquée des mots de passe
