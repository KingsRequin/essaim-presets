"""Reconstruit index.json, la liste lue par Essaim, à partir de presets/*.toml.

Lancé par le workflow « Index » à chaque changement de presets/ ou d'apercus/ sur main ; se lance
aussi à la main : python scripts/index.py

Pour chaque preset : `nom` est le nom du fichier, `reglages` son contenu (sans [rendu]), `apercu`
l'image apercus/<nom>.gif ou .png si elle existe. `auteur` (compte GitHub qui a ajouté le fichier)
et `etiquettes` sont gardés de l'index précédent : on peut les corriger à la main dans index.json.
"""
import json
import os
import pathlib
import sys
import tomllib
import urllib.parse
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent.parent
INDEX = RACINE / "index.json"
# bornes d'Essaim (ui/app.js) : un index qui les dépasse n'est pas chargé en entier
NOM_MAX, PRESETS_MAX, INDEX_MAX = 40, 500, 1 << 20
HORS_INDEX = {"rendu"}


def avertir(message, fichier=None):
    """Avertissement, visible dans le résumé du workflow."""
    print(f"::warning{f' file={fichier}' if fichier else ''}::{message}")


def auteur(fichier):
    """Compte GitHub de la personne qui a ajouté `fichier` au dépôt ("" hors du workflow)."""
    depot, jeton = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (depot and jeton):
        return ""
    url = f"https://api.github.com/repos/{depot}/commits?per_page=100&path={urllib.parse.quote(fichier)}"
    demande = urllib.request.Request(url, headers={"Authorization": f"Bearer {jeton}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(demande, timeout=20) as reponse:
            commits = json.load(reponse)
        # du plus récent au plus ancien : le dernier est celui qui a créé le fichier
        return ((commits[-1].get("author") or {}).get("login") or "") if commits else ""
    except (OSError, ValueError) as e:
        avertir(f"auteur de {fichier} introuvable ({e})", fichier)
        return ""


def apercu(nom):
    for ext in ("gif", "png"):
        if (RACINE / "apercus" / f"{nom}.{ext}").is_file():
            return f"apercus/{nom}.{ext}"
    return ""


def construire():
    try:
        avant = {p["fichier"]: p for p in json.loads(INDEX.read_text(encoding="utf-8"))["presets"] if isinstance(p, dict) and "fichier" in p}
    except (OSError, ValueError, KeyError, TypeError):
        avant = {}
    presets, noms = [], set()
    for f in sorted((RACINE / "presets").glob("*.toml"), key=lambda f: f.stem.casefold()):
        chemin, nom = f"presets/{f.name}", f.stem.strip()
        if not nom or len(nom) > NOM_MAX:
            avertir(f"{chemin} : nom vide ou de plus de {NOM_MAX} caractères, preset ignoré", chemin)
            continue
        if nom.casefold() in noms:
            avertir(f"{chemin} : un autre preset porte déjà ce nom, preset ignoré", chemin)
            continue
        try:
            contenu = tomllib.loads(f.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError) as e:
            avertir(f"{chemin} : TOML illisible ({e}), preset ignoré", chemin)
            continue
        ancien = avant.get(chemin, {})
        entree = {
            "nom": nom,
            "auteur": ancien["auteur"] if isinstance(ancien.get("auteur"), str) and ancien["auteur"] else auteur(chemin),
            "etiquettes": ancien["etiquettes"] if isinstance(ancien.get("etiquettes"), list) else [],
            "fichier": chemin,
        }
        if image := apercu(nom):
            entree["apercu"] = image
        # seules les sections (tables) comptent pour Essaim
        entree["reglages"] = {s: v for s, v in contenu.items() if isinstance(v, dict) and s not in HORS_INDEX}
        noms.add(nom.casefold())
        presets.append(entree)
    if len(presets) > PRESETS_MAX:
        avertir(f"{len(presets)} presets : Essaim n'en montre que {PRESETS_MAX}")
    # un preset par ligne : les différences restent lisibles
    lignes = ",\n".join("  " + json.dumps(p, ensure_ascii=False) for p in presets)
    return '{"version": 1, "presets": [' + (f"\n{lignes}\n" if presets else "") + "]}\n", len(presets)


def main():
    texte, nombre = construire()
    json.loads(texte)
    if len(texte.encode("utf-8")) > INDEX_MAX:
        sys.exit(f"::error::index.json dépasserait {INDEX_MAX} octets : Essaim ne le chargerait plus")
    INDEX.write_bytes(texte.encode("utf-8"))
    print(f"index.json : {nombre} preset(s)")


if __name__ == "__main__":
    main()
