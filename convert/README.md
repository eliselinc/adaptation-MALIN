# Conversion

Convertir des exercices ou manuels adaptés d'un format à l'autre :
- Cartable (Cahiers Fantastiques)
- MALIN
___

## Conversion d'un manuel entier

#### Conversion d'un manuel : HTML Cartable → MALIN

Dans `adaptation-MALIN` :
```bash
python3 convert/main.py <textbook> --input_format cartable
```

- Argument textbook : 1 répertoire correspondant à 1 manuel. Ce répertoire contient un sous-dossier `json` avec les exercices .js au format Cartable
- Sorties :
    - Fichiers individuels JSON MALIN : `./<textbook>/json_malin/*.json`
    - Fichiers individuels HTML MALIN : `./<textbook>/html_malin/*.html`
    - Fichier HTML MALIN du manuel complet :`./<textbook>/html_malin/<textbook>.html`

Exemple d'exécution :
```bash
python3 convert/main.py ./manuels/CM1_francais --input_format cartable
```

#### Conversion d'un manuel : Exercices individuels JSON MALIN → HTML MALIN

Dans `adaptation-MALIN` :
```bash
python3 convert/main.py <input_textbook> --input_format malin
```
- Argument textbook : 1 répertoire correspondant à 1 manuel. Ce répertoire contient un sous-dossier `json_malin` avec les exercices .json au format MALIN
- Sorties :
    - Fichiers individuels HTML MALIN : `./<textbook>/html_malin/*.html`
    - Fichier HTML MALIN du manuel complet :`./<textbook>/html_malin/<textbook>.html`

Exemple d'exécution :
```bash
python3 convert/main.py ./manuels/CM1_francais --input_format malin
```

#### Conversion d'un manuel : Manuel HTML MALIN autonome → Exercices individuels JSON MALIN

Dans `adaptation-MALIN` :
```bash
python3 convert/main.py <<textbook>/filename.html>
```
- Argument : un unique fichier HTML du manuel au format MALIN 
- Sortie :
    - Fichiers individuels JSON MALIN : `./<textbook>/json_malin/*.json`

Exemple d'exécution :
```bash
python3 convert/main.py ./manuels/CM1_francais/CM1_francais.html
```

#### Organisation du répertoire (1 répertoire = 1 manuel)

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
___

## Conversion d'un exercice spécifique

#### Conversion d'un exercice spécifique : Exercice individuel JSON MALIN → Exercice individuel HTML MALIN

Dans `adaptation-MALIN` :
```bash
python3 convert/main.py <input_folder> --input_format malin --ex_id <ex_id>
```
- Arguments :
  - Input folder : répertoire contenant un sous-dossier `json_malin` avec les exercices .json au format MALIN
  - Input format : `malin`
  - Ex id : identifiant de l'exercice (nom du fichier sans l'extension)
- Sortie :
    - Fichiers individuels JSON MALIN : `./<textbook>/json_malin/*.json`

Exemple d'exécution :
```bash
python3 convert/main.py ./manuels/CM1_francais --input_format malin --ex_id P7Ex2

python3 convert/main.py ./exercices/CM/ --input_format malin --ex_id CE2_P20Ex6
```