"""Exécuter les blocs B/C et conserver les résultats réels, puis restaurer le modèle."""

import json
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault("PREFECT_API_URL", "http://127.0.0.1:4200/api")

from flow_mlops import reentrainement
from verifier_qualite import controler_f1

RACINE = Path(__file__).resolve().parent


def executer(nom, profondeur, attendu):
    etat = reentrainement.with_options(flow_run_name=nom)(return_state=True)
    run_id = str(etat.state_details.flow_run_id)
    mets = json.loads((RACINE / "reports/metrics.json").read_text(encoding="utf-8"))
    verification = subprocess.run(
        [sys.executable, str(RACINE / "verifier_qualite.py")],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8",
    )
    resultat = {
        "nom": nom, "max_depth": profondeur, "flow_run_id": run_id,
        "etat": etat.name, "metriques": mets,
        "code_verification": verification.returncode,
        "sortie_verification": verification.stdout,
    }
    print(json.dumps(resultat, ensure_ascii=False), flush=True)
    if etat.name != attendu:
        raise RuntimeError(f"Etat inattendu pour {nom}: {etat.name}")
    if verification.returncode != (0 if attendu == "Completed" else 1):
        raise RuntimeError("Code de retour inattendu pour la verification CI")
    return resultat


def main():
    params = RACINE / "params.yaml"
    original = params.read_bytes()
    if b"max_depth: 12" not in original:
        raise RuntimeError("L'etat initial doit contenir max_depth: 12")
    for f1 in (0.82, 0.8423):
        assert controler_f1(f1, 0.82)
    for f1 in (0.25, float("nan"), float("inf")):
        try:
            controler_f1(f1, 0.82)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Score invalide accepte : {f1}")
    resultats = []
    try:
        resultats.append(executer("TP6-B-modele-valide", 12, "Completed"))
        params.write_bytes(original.replace(b"max_depth: 12", b"max_depth: 2"))
        resultats.append(executer("TP6-C-modele-refuse", 2, "Failed"))
    finally:
        params.write_bytes(original)
        resultats.append(executer("TP6-C-modele-restaure", 12, "Completed"))
        (RACINE / "reports/essais_tp6.json").write_text(
            json.dumps(resultats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
