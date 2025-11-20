# Conversion

Convertir des exercices ou manuels adaptés d'un format à l'autre :
- Cartable (Cahiers Fantastiques)
- MALIN

## Running

**Commande**

Dans `adaptation-MALIN` :
```bash
python3 convert/convert.py <input_textbook> <input_format>
```

**Arguments**

- Input textbook : 1 répertoire ou fichier correspondant à 1 manuel
- Input format : `cartable` ou `malin` (ou rien)

**Cas**
- Si `cartable` : 
  - Le dossier d'entrée contient un sous-dossier `json` avec les exercices .js au format Cartable
  - Sorties :
    - Fichiers individuels JSON MALIN : `./<textbook>/json_malin/*.json`
    - Fichiers individuels HTML MALIN : `./<textbook>/html_malin/*.html`
    - Fichier HTML MALIN du manuel complet :`./<textbook>/html_malin/<textbook>.html`
- Si `malin` : 
  - Le dossier d'entrée contient un sous-dossier `json_malin` avec les exercices .json au format MALIN
  - Sorties :
    - Fichiers individuels HTML MALIN : `./<textbook>/html_malin/*.html`
    - Fichier HTML MALIN du manuel complet :`./<textbook>/html_malin/<textbook>.html`
- Si pas de format spécifié : 
  - L'entrée est un unique fichier HTML du manuel au format MALIN 
  - Sortie :
    - Fichiers individuels JSON MALIN : `./<textbook>/json_malin/*.json`

**Exemples d'exécution**

```bash
python3 convert/convert.py ../data/manuel_CM1_francais --input_format cartable

python3 convert/convert.py ../data/manuel_CM1_francais/textbook.html
```

**Organisation d'un répertoire (1 répertoire = 1 manuel)**

```yaml
<textbook>
 |
 ├── *.html             # HTML Cartable
 ├── json               # JSON Cartable
 ├── communs            # CSS et styles Cartable
 ├── medias             # Images utilisée dans les exercices Cartable
 |
 ├── json_malin         # JSON MALIN (fichiers individuels)
 ├── html_malin         # HTML MALIN (fichiers individuels)
 └── <textbook>.html    # HTML MALIN, manuel complet dans 1 fichier unique
```