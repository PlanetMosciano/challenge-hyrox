#!/usr/bin/env python3
"""Aggiorna i risultati della pagina Share your Race – Simulazione Gara HYROX.

Uso: python3 simulazione/aggiorna.py stato.json [GG.MM.AAAA]

stato.json = documento gara/stato dell'artifact "Cronometro Gara"
(slug 633c28e3-d299-44f5-8150-22fff35bcffc), con i campi athletes, names, sex.
Pubblica solo gli atleti arrivati (partenza e arrivo presenti) con sesso M/F.
Tocca SOLO il blocco <script id="results"> di simulazione/index.html.
"""
import json, re, sys, datetime, zoneinfo, pathlib

src = json.load(open(sys.argv[1], encoding="utf-8"))
now = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Rome"))
date = sys.argv[2] if len(sys.argv) > 2 else now.strftime("%d.%m.%Y")

ath, names, sex = src.get("athletes") or {}, src.get("names") or {}, src.get("sex") or {}
out = []
for n, a in ath.items():
    if not isinstance(a, dict) or not a.get("start") or not a.get("finish"):
        continue
    s = {"M": "U", "F": "D"}.get(sex.get(n))
    if not s:
        continue
    ms = int(a["finish"]) - int(a["start"])
    if ms <= 0:
        continue
    out.append({"name": (names.get(n) or f"Atleta {n}")[:40], "sex": s, "ms": ms})
out.sort(key=lambda x: x["name"].lower())

res = {"athletes": out, "event": {"date": date}, "updated": now.strftime("%d/%m/%Y %H:%M")}
blob = json.dumps(res, ensure_ascii=False).replace("</", "<\\/")

p = pathlib.Path(__file__).with_name("index.html")
html = p.read_text(encoding="utf-8")
m = re.search(r'<script id="results" type="application/json">(.*?)</script>', html, flags=re.S)
try:
    prev = json.loads(m.group(1)) if m else {}
except Exception:
    prev = {}
if prev.get("athletes") == out and (prev.get("event") or {}).get("date") == date:
    print(f"nessuna modifica ({len(out)} atleti)")
    sys.exit(0)
new, k = re.subn(r'(<script id="results" type="application/json">).*?(</script>)',
                 lambda m: m.group(1) + blob + m.group(2), html, count=1, flags=re.S)
if k != 1:
    sys.exit("blocco results non trovato")
p.write_text(new, encoding="utf-8")
print(f"{len(out)} atleti pubblicati, aggiornato {res['updated']}")
