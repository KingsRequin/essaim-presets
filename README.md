# Presets d'Essaim

Bibliothèque communautaire de presets pour [Essaim](https://github.com/KingsRequin/essaim),
la surcouche réactive à la musique autour du pointeur. Essaim lit `index.json` (branche `main`)
et montre ces presets dans l'onglet *Presets*, source *Bibliothèque communautaire*.

*Community preset library for [Essaim](https://github.com/KingsRequin/essaim). To share a
preset: tick "Publish" when saving it in Essaim, then confirm the pull request GitHub opens.*

## Proposer un preset

1. Dans Essaim, enregistre tes réglages comme preset en cochant **Publier**.
2. GitHub s'ouvre sur la création de `presets/<nom>.toml`, déjà rempli. Un preset trop long
   pour l'adresse est copié dans le presse-papiers : colle-le (Ctrl+V) dans le fichier.
3. Valide (*Commit changes*, puis *Propose changes*) : GitHub fait une copie du dépôt à ton nom
   et ouvre une pull request.
4. Après relecture, le preset est ajouté à l'index et apparaît dans la bibliothèque de tout le
   monde.

Sans Essaim sous la main : exporte le preset (fichier `.toml`) et dépose-le dans `presets/` par
une pull request.

## Contenu du dépôt

- `presets/<nom>.toml` : les presets, tels qu'Essaim les enregistre ;
- `apercus/<nom>.png` ou `.gif` (facultatif) : image montrée dans la vignette ;
- `index.json` : la liste lue par Essaim.

```json
{"version": 1, "presets": [
  {"nom": "Pollen", "auteur": "pseudo-github", "etiquettes": ["dense", "jaune"],
   "fichier": "presets/Pollen.toml", "apercu": "apercus/Pollen.gif",
   "reglages": {"orbite": {"rayon": 26}, "essaim": {"maximum": 40}, "couleur": {"teinte": 50, "vitesse_teinte": 0}}}
]}
```

`reglages` reprend les sections du fichier `.toml` (sauf `[rendu]`) ; les clés absentes prennent
les valeurs du preset *Défaut*. Le format complet est décrit dans le
[guide d'Essaim](https://github.com/KingsRequin/essaim/blob/master/docs/guide.md#bibliothèque-de-presets-github).
