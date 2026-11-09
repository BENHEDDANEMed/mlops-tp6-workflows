"""Même règle de qualité pour Prefect et GitHub Actions."""

import json
import math
from pathlib import Path
import sys

import yaml

RACINE = Path(__file__).resolve().parent


def controler_f1(f1, seuil):
    for nom, valeur in (("F1", f1), ("seuil", seuil)):
        if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
            raise ValueError(f"{nom} doit etre un nombre")
        if not math.isfinite(valeur) or not 0 <= valeur <= 1:
            raise ValueError(f"{nom} doit etre fini et compris entre 0 et 1")
    if f1 < seuil:
        raise ValueError(f"F1 {f1} < seuil {seuil} : modele refuse")
    return True


def main():
    with (RACINE / "reports/metrics.json").open(encoding="utf-8") as fichier:
        f1 = json.load(fichier)["f1"]
    with (RACINE / "params.yaml").open(encoding="utf-8") as fichier:
        seuil = yaml.safe_load(fichier)["validation"]["seuil_f1"]
    print(f"F1 = {f1} | seuil = {seuil}")
    try:
        controler_f1(f1, seuil)
    except ValueError as erreur:
        print(f"ECHEC : {erreur}")
        return 1
    print("OK : modele accepte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
