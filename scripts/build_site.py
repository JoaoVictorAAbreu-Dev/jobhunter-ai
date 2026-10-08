"""Build a privacy-conscious static GitHub Pages job board."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SITE.mkdir(parents=True, exist_ok=True)
CSV_PATH = ROOT / "vagas_para_revisar.csv"
FIELDS = ("empresa", "titulo", "nivel", "local", "modalidade", "area", "pontuacao", "url")
if CSV_PATH.exists():
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
else:
    rows = []
public = [{key: row.get(key, "") for key in FIELDS} for row in rows]
(SITE / "vagas.json").write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")
(SITE / "index.html").write_text((ROOT / "web" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
(SITE / "styles.css").write_text((ROOT / "web" / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")
print(f"Site gerado com {len(public)} vagas públicas")
