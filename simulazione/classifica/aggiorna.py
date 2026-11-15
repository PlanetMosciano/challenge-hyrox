#!/usr/bin/env python3
"""Aggiorna la classifica pubblica (OptiSigns) della Simulazione Gara HYROX.

Uso: python3 simulazione/classifica/aggiorna.py stato.json
stato.json = db_get gara/stato dell'artifact "Cronometro Gara" (slug 633c28e3-d299-44f5-8150-22fff35bcffc).
Scrive SOLO simulazione/classifica/dati.json (atleti partiti: start/finish, nomi, sesso, titolo).
"""
import json, sys, datetime, zoneinfo, pathlib
src = json.load(open(sys.argv[1], encoding="utf-8"))
ath = {k: {x: v[x] for x in ("start", "finish") if v.get(x)} for k, v in (src.get("athletes") or {}).items()
       if isinstance(v, dict) and v.get("start")}
names = {k: str(v)[:40] for k, v in (src.get("names") or {}).items() if k in ath}
sex = {k: v for k, v in (src.get("sex") or {}).items() if k in ath and v in ("M", "F")}
title = str(src.get("title") or "")[:60]
p = pathlib.Path(__file__).with_name("dati.json")
try:
    prev = json.loads(p.read_text(encoding="utf-8"))
except Exception:
    prev = {}
if prev.get("athletes") == ath and prev.get("names") == names and prev.get("sex") == sex and prev.get("title") == title:
    print(f"nessuna modifica ({len(ath)} partiti)"); sys.exit(0)
now = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Rome")).strftime("%H:%M")
p.write_text(json.dumps({"athletes": ath, "names": names, "sex": sex, "title": title, "updated": now}, ensure_ascii=False), encoding="utf-8")
fin = sum(1 for a in ath.values() if a.get("finish"))
print(f"{len(ath)} partiti, {fin} arrivati, aggiornato {now}")
