#!/usr/bin/env python3
"""Prüft belegte Extraktionen und erzeugt einen Markdown-Garten. Nur Standardbibliothek."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import difflib
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ORDNER = {"Projekt": "projekte", "Massnahme": "massnahmen", "Erkenntnis": "erkenntnisse",
          "Kontext": "kontexte", "Zielgruppe": "zielgruppen", "Quelle": "quellen", "Barriere": "barrieren"}


class GartenFehler(Exception):
    pass


def lesen(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def jsontext(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normal(text):
    return " ".join(text.split())


def sicherer_pfad(path):
    p = (ROOT / path).resolve()
    if not p.is_relative_to(ROOT):
        raise GartenFehler(f"Pfad liegt außerhalb des Gartens: {path}")
    return p


def schema_laden(version):
    path = ROOT / "ontologie" / f"{version}.json"
    if not path.is_file():
        raise GartenFehler(f"Ontologie fehlt: {version}")
    return lesen(path)


class Haupttext(HTMLParser):
    def __init__(self):
        super().__init__()
        self.main = 0
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.main += 1
        if tag in ("script", "style"):
            self.skip += 1
        if self.main and tag in ("p", "h1", "h2", "h3", "li", "div"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "main":
            self.main -= 1
        if tag in ("script", "style"):
            self.skip -= 1
        if self.main and tag in ("p", "h1", "h2", "h3", "li", "div"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.main and not self.skip:
            self.parts.append(data)

    def text(self):
        return "\n".join(s.strip() for s in "".join(self.parts).splitlines() if s.strip()) + "\n"


def text_extrahieren(original, fmt):
    if fmt == "pdf":
        if not shutil.which("pdftotext"):
            raise GartenFehler("Für neue PDF-Quellen fehlt pdftotext. Die vorbereitete Demo braucht dieses Programm nicht.")
        r = subprocess.run(["pdftotext", "-layout", str(original), "-"], check=True, capture_output=True)
        return r.stdout.decode("utf-8")
    if fmt == "html":
        p = Haupttext()
        p.feed(original.read_text(encoding="utf-8"))
        result = p.text()
        if not result.strip():
            raise GartenFehler("Kein HTML-Hauptinhalt gefunden. Erstelle stattdessen eine geprüfte UTF-8-Textquelle.")
        return result
    return original.read_text(encoding="utf-8")


def text_markdown(q, text):
    out = [f"# {q['id']} – Text der Originalquelle", "", f"Herkunft: {q['url']}", "",
           "Automatisch extrahierter Text. Die PDF-Seite zählt ab der ersten Dateiseite. Bei Layoutfragen gilt das Original.", ""]
    pages = text.split("\f") if q["format"] == "pdf" else [text]
    if pages and not pages[-1].strip():
        pages.pop()
    for i, page in enumerate(pages, 1):
        out += [f"## PDF-Seite {i}" if q["format"] == "pdf" else "## Hauptinhalt", "", "````text", page.rstrip(), "````", ""]
    return "\n".join(out) + "\n"


def registrieren(args):
    ident = args.id
    if not re.fullmatch(r"Q\d{2,}", ident):
        raise GartenFehler("Quellenkennung muss Q und mindestens zwei Ziffern enthalten.")
    manifest_path = ROOT / "raw/manifest.json"
    manifest = lesen(manifest_path)
    if any(q["id"] == ident for q in manifest):
        raise GartenFehler(f"Quelle {ident} ist bereits registriert. Nutze eine neue Kennung für eine neue Fassung.")
    src = Path(args.datei).resolve()
    fmt = src.suffix.lstrip(".").lower()
    if fmt not in ("pdf", "html", "txt", "md"):
        raise GartenFehler("Erlaubt sind PDF, HTML und UTF-8-Text als TXT oder Markdown.")
    if fmt == "pdf" and not src.read_bytes().startswith(b"%PDF"):
        raise GartenFehler("Die Datei ist kein PDF.")
    # Erst extrahieren. Bei Fehlern entsteht kein teilweise registrierter Datensatz.
    text = text_extrahieren(src, fmt)
    if not text.strip():
        raise GartenFehler("Die Quelle enthält keinen extrahierbaren Text. Ein Scan braucht Texterkennung.")
    original = ROOT / "raw/originale" / f"{ident}.{fmt}"
    txt = ROOT / "raw/texte" / f"{ident}.txt"
    md = ROOT / "raw/texte" / f"{ident}.md"
    if any(p.exists() for p in (original, txt, md)):
        raise GartenFehler("Eine Zieldatei existiert bereits. Vorhandene Quellen werden nicht überschrieben.")
    q = dict(id=ident, titel=args.titel, herausgeber=args.herausgeber, publikationsjahr=args.jahr,
             url=args.url, format=fmt, phase=args.phase, original=original.relative_to(ROOT).as_posix(),
             abgerufen_am=datetime.now(timezone.utc).isoformat(timespec="seconds"),
             rechte="Fremdquelle. Rechte verbleiben beim Herausgeber.")
    shutil.copyfile(src, original)
    txt.write_text(text, encoding="utf-8")
    md.write_text(text_markdown(q, text), encoding="utf-8")
    q.update(sha256=sha(original), bytes=original.stat().st_size, text=txt.relative_to(ROOT).as_posix(),
             text_sha256=sha(txt), lesetext=md.relative_to(ROOT).as_posix(), lesetext_sha256=sha(md))
    manifest.append(q)
    manifest_path.write_text(jsontext(manifest), encoding="utf-8")
    print(f"{ident} gesichert. Nächster Schritt: Extraktion mit Belegen erstellen.")


def quellen_pruefen(manifest):
    errors = []
    seen = set()
    for q in manifest:
        if q["id"] in seen:
            errors.append(f"Doppelte Quellenkennung: {q['id']}")
        seen.add(q["id"])
        for key, hashkey in (("original", "sha256"), ("text", "text_sha256"), ("lesetext", "lesetext_sha256")):
            if key not in q or hashkey not in q:
                errors.append(f"{q['id']}: Sicherungsfeld fehlt: {key}/{hashkey}")
                continue
            path = sicherer_pfad(q[key])
            if not path.is_file() or sha(path) != q[hashkey]:
                errors.append(f"{q['id']}: Datei fehlt oder Prüfsumme weicht ab: {q[key]}")
    return errors


def zusammenfuehren(pakete, manifest):
    quellen = {q["id"]: q for q in manifest}
    nodes, evidence, edges, used = {}, {}, {}, []
    for path in pakete:
        packet = lesen(path)
        qid = packet["quelle"]
        if qid not in quellen:
            raise GartenFehler(f"Quelle ist nicht registriert: {qid}")
        if qid in used:
            raise GartenFehler(f"Mehrere Pakete für dieselbe Quelle: {qid}")
        used.append(qid)
        if packet.get("status") not in ("fachlich-ungeprueft", "fachlich-geprueft", "strittig"):
            raise GartenFehler(f"{qid}: Unbekannter Prüfstatus")
        for b in packet["belege"]:
            bid = f"{qid}:{b['id']}"
            if bid in evidence:
                raise GartenFehler(f"Doppelter Beleg: {bid}")
            evidence[bid] = dict(b, quelle=qid)
        for node in packet["entitaeten"]:
            node = copy.deepcopy(node)
            node.setdefault("status", packet["status"])
            if node["id"] in nodes:
                old = nodes[node["id"]]
                # Identitäten werden ergänzt. Abweichende Aussagen brauchen eine eigene Erkenntnis.
                for key in set(old) | set(node):
                    if key == "belege":
                        continue
                    if old.get(key) != node.get(key):
                        raise GartenFehler(f"Identitätskonflikt bei {node['id']}, Feld {key}. Fachlich klären.")
                old["belege"] = sorted(set(old["belege"] + node["belege"]))
            else:
                nodes[node["id"]] = node
        for edge in packet["beziehungen"]:
            key = (edge["von"], edge["relation"], edge["nach"])
            if key in edges:
                edges[key]["belege"] = sorted(set(edges[key]["belege"] + edge["belege"]))
            else:
                edges[key] = copy.deepcopy(edge)
    for qid in used:
        q = quellen[qid]
        if qid in nodes:
            raise GartenFehler(f"Quellenkennung als Fachentität verwendet: {qid}")
        nodes[qid] = dict(id=qid, typ="Quelle", titel=q["titel"], kurztext=f"Original von {q['herausgeber']}.",
                          belege=[], status="fachlich-ungeprueft")
    # Herkunft ist selbst eine typisierte Beziehung. Originalquellen brauchen keinen Selbstbeleg.
    for node in nodes.values():
        for qid in sorted({b.split(":")[0] for b in node["belege"]}):
            key = (node["id"], "belegt_durch", qid)
            edges[key] = dict(von=node["id"], relation="belegt_durch", nach=qid,
                              belege=[b for b in node["belege"] if b.startswith(qid + ":")])
    return dict(entitaeten=nodes, belege=evidence, beziehungen=list(edges.values()), quellen=used)


def validieren(graph, schema, manifest):
    errors = []
    nodes = graph["entitaeten"]
    sources = {q["id"]: q for q in manifest}
    for bid, b in graph["belege"].items():
        q = sources[b["quelle"]]
        text = sicherer_pfad(q["text"]).read_text(encoding="utf-8")
        if q["format"] == "pdf":
            pages = text.split("\f")
            page = b.get("seite")
            if not isinstance(page, int) or isinstance(page, bool) or not 1 <= page <= len(pages):
                errors.append(f"{bid}: Ungültige PDF-Seite")
                continue
            text = pages[page - 1]
        elif not b.get("abschnitt") or normal(b["abschnitt"]) not in normal(text):
            errors.append(f"{bid}: Abschnitt fehlt oder ist nicht im Text enthalten")
        if not b.get("suchtext") or normal(b["suchtext"]) not in normal(text):
            errors.append(f"{bid}: Suchtext fehlt an der angegebenen Fundstelle")
        if not b.get("aussage"):
            errors.append(f"{bid}: Belegaussage fehlt")
    def belege_pruefen(obj, label):
        if not obj.get("belege"):
            errors.append(f"{label}: Beleg fehlt")
        for bid in obj.get("belege", []):
            if bid not in graph["belege"]:
                errors.append(f"{label}: Unbekannter Beleg {bid}")
    for ident, node in nodes.items():
        if not re.fullmatch(r"[A-Z]\d{2,}", ident):
            errors.append(f"Ungültige Kennung: {ident}")
        for key in schema["pflichtfelder"]:
            if key not in node:
                errors.append(f"{ident}: Pflichtfeld fehlt: {key}")
        if node.get("typ") not in schema["typen"]:
            errors.append(f"{ident}: Unbekannter Typ {node.get('typ')}")
        if node.get("status") not in schema["statuswerte"]:
            errors.append(f"{ident}: Ungültiger Status")
        if node.get("typ") != "Quelle":
            belege_pruefen(node, ident)
        if node.get("typ") == "Erkenntnis":
            for key in schema["erkenntnisfelder"]:
                if not node.get(key):
                    errors.append(f"{ident}: Erkenntnisfeld fehlt: {key}")
            if node.get("aussageart") not in schema["aussagearten"]:
                errors.append(f"{ident}: Unbekannte Aussageart")
            for rel in schema["pflichtrelationen"]["Erkenntnis"]:
                if not any(e["von"] == ident and e["relation"] == rel for e in graph["beziehungen"]):
                    errors.append(f"{ident}: Pflichtbeziehung fehlt: {rel}")
    for edge in graph["beziehungen"]:
        label = f"{edge['von']} – {edge['relation']} – {edge['nach']}"
        belege_pruefen(edge, label)
        if edge["von"] not in nodes or edge["nach"] not in nodes:
            errors.append(f"{label}: Ziel oder Ausgangspunkt fehlt")
            continue
        rule = schema["relationen"].get(edge["relation"])
        if not rule:
            errors.append(f"{label}: Unbekannte Beziehung")
        elif nodes[edge["von"]]["typ"] not in rule["von"] or nodes[edge["nach"]]["typ"] not in rule["nach"]:
            errors.append(f"{label}: Beziehung hat unzulässige Typen")
    return errors


def knotenpfad(node):
    return f"{ORDNER.get(node['typ'], 'weitere')}/{node['id']}.md"


def wikilink(path, label=None, anchor=""):
    target = Path(path).as_posix()
    if target.endswith(".md"):
        target = target[:-3]
    return f"[[{target}{'#' + anchor if anchor else ''}|{label or Path(target).name}]]"


def link(out, node):
    return wikilink((out / knotenpfad(node)).relative_to(ROOT), node["titel"])


def zitate(out, graph, bids):
    return "; ".join(wikilink((out / f"quellen/{bid.split(':')[0]}.md").relative_to(ROOT), bid,
                             bid.split(":")[1]) for bid in sorted(set(bids)))


def frage_auswerten(question, graph, schema, out):
    query = question["abfrage"]
    rel = query.get("relation")
    follow = query.get("folgebeziehung")
    required = query.get("erfordert_typ")
    if ((required and required not in schema["typen"]) or (rel and rel not in schema["relationen"])
            or (follow and follow["relation"] not in schema["relationen"])):
        return "modellluecke", "**Modelllücke:** Diese Frage braucht einen weiteren Typ oder eine weitere Beziehung. Ein Kontext als Freitext liefert noch keine typisierte Zuordnung."
    nodes = graph["entitaeten"]
    if query.get("typ"):
        hits = [n for n in nodes.values() if n["typ"] == query["typ"]]
        edges = []
    else:
        edges = [e for e in graph["beziehungen"] if e["relation"] == rel and (not query.get("ziel") or e["nach"] == query["ziel"])]
        if follow:
            edges = [e for e in edges if any(f["von"] == e["nach"] and f["relation"] == follow["relation"] and f["nach"] == follow["ziel"] for f in graph["beziehungen"])]
        hits = [nodes[x] for x in sorted({e["von"] for e in edges})] if query.get("ziel") else []
    if not hits and not edges:
        return "keine_belege", question["leertext"]
    lines = []
    if hits:
        for node in sorted(hits, key=lambda n: n["id"]):
            text = node["grenzen"] if query.get("nur_grenzen") else node.get("beobachtung", node["kurztext"])
            lines.append(f"- {link(out, node)}: {text} Belege: {zitate(out, graph, node['belege'])}.")
            if node["typ"] == "Erkenntnis" and not query.get("nur_grenzen"):
                lines.append(f"  Übertragbarkeit: {node['uebertragbarkeit']} Grenze: {node['grenzen']}")
    else:
        for edge in edges:
            lines.append(f"- {link(out, nodes[edge['von']])} → **{edge['relation']}** → {link(out, nodes[edge['nach']])}. Belege: {zitate(out, graph, edge['belege'])}.")
    return "beantwortet", "\n".join(lines)


def frontmatter(data):
    return "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in data.items()) + "\n---\n\n"


def rendern(graph, schema, manifest, out):
    files = {}
    nodes = graph["entitaeten"]
    sources = {q["id"]: q for q in manifest}
    index = ["# Knowledge Garden", "", f"Ontologie: **{schema['version']}** · {len(graph['quellen'])} Quellen · {len(nodes)} Seiten mit Typ.", "",
             "> Demonstration mit echten Quellen. Fachliche Prüfung steht aus. Aussagen bleiben an ihre Bedingungen gebunden.", "",
             "## Fragen stellen", "", "Die folgenden Antworten entstehen aus strukturierten Beziehungen. Freie Fragen bearbeitet der KI-Agent mit dem Frage-Prompt.", ""]
    for question in lesen(ROOT / "ontologie/fragen.json"):
        status, answer = frage_auswerten(question, graph, schema, out)
        index.append(f"- {wikilink((out / ('fragen/' + question['id'] + '.md')).relative_to(ROOT), question['id'] + ': ' + question['frage'])} · `{status}`")
        files[f"fragen/{question['id']}.md"] = frontmatter(dict(typ="abfrage", status=status, ontologie=schema["version"])) + f"# {question['frage']}\n\nStrukturierte Abfrage `{question['id']}`. Fachlich ungeprüfte Zusammenstellung.\n\n{answer}\n\nZurück: {wikilink((out / 'index.md').relative_to(ROOT), 'Gartenübersicht')}\n"
    for typ in schema["typen"]:
        index += ["", f"## {typ}", ""]
        for node in sorted(nodes.values(), key=lambda n: n["id"]):
            if node["typ"] == typ:
                index.append(f"- {link(out, node)} — {node['kurztext']}")
    index += ["", "## Stand und Herkunft", "", f"{wikilink((out / 'log.md').relative_to(ROOT), 'Verarbeitungsstand')} · [[ONTOLOGY|Modell und Regeln]] · [[demo/ABLAUF|Vorführung]]", ""]
    files["index.md"] = "\n".join(index)
    for node in nodes.values():
        ident = node["id"]
        meta = dict(id=ident, typ=node["typ"], status=node["status"], ontologie=schema["version"],
                    quellen=[wikilink((out / f"quellen/{q}.md").relative_to(ROOT), q) for q in sorted({b.split(':')[0] for b in node["belege"]})])
        lines = [f"# {node['titel']}", "", node["kurztext"], "", "> Fachlich ungeprüft. Herkunft und technische Prüfung ersetzen keine fachliche Prüfung.", ""]
        if node["typ"] == "Quelle":
            q = sources[ident]
            origin = os.path.relpath(ROOT / q["original"], out / "quellen")
            readtext = wikilink(Path(q["lesetext"]), "Extrahierten Text öffnen")
            lines += [f"- Herausgeber: {q['herausgeber']}", f"- Publikationsjahr: {q.get('publikationsjahr') or 'nicht festgestellt'}",
                      f"- Abruf: {q['abgerufen_am']}", f"- Original im Web: [Herausgeberquelle]({q['url']})",
                      f"- Lokale Datei: [Gesichertes Original](<{origin}>)", f"- Lesetext: {readtext}",
                      f"- SHA-256: `{q['sha256']}`", f"- Rechte: {q['rechte']}", ""]
            for bid, b in sorted(graph["belege"].items()):
                if b["quelle"] != ident:
                    continue
                lines += [f"## {b['id']}", "", b["aussage"], ""]
                if q["format"] == "pdf":
                    lines += [f"Fundstelle: [PDF-Seite {b['seite']}](<{origin}#page={b['seite']}>) · " + wikilink(Path(q["lesetext"]), "Text der Seite", f"PDF-Seite {b['seite']}"), ""]
                else:
                    lines += [f"Fundstelle: Abschnitt „{b['abschnitt']}“ im gesicherten Hauptinhalt.", ""]
                lines += [f"Suchtext zur Prüfung: `{b['suchtext']}`", ""]
        if node["typ"] == "Erkenntnis":
            lines += [f"Aussageart: **{node['aussageart']}**", ""]
            for key, heading in (("beobachtung", "Beobachtung in der Quelle"), ("interpretation", "Interpretation der KI"),
                                 ("uebertragbarkeit", "Übertragbarkeit prüfen"), ("grenzen", "Grenzen der Evidenz"), ("offene_frage", "Offene Frage")):
                lines += [f"## {heading}", "", node[key], ""]
        if node["belege"]:
            lines += ["## Belege", "", zitate(out, graph, node["belege"]), ""]
        lines += ["## Beziehungen", ""]
        for edge in graph["beziehungen"]:
            if edge["von"] == ident:
                note = f" ({edge['einordnung']})" if edge.get("einordnung") else ""
                lines += [f"- **{edge['relation']}** → {link(out, nodes[edge['nach']])}{note}. {zitate(out, graph, edge['belege'])}"]
        lines += ["", "## Eingehende Beziehungen", ""]
        for edge in graph["beziehungen"]:
            if edge["nach"] == ident:
                note = f" ({edge['einordnung']})" if edge.get("einordnung") else ""
                lines += [f"- {link(out, nodes[edge['von']])} → **{edge['relation']}**{note}. {zitate(out, graph, edge['belege'])}"]
        lines += ["", f"Zurück: {wikilink((out / 'index.md').relative_to(ROOT), 'Gartenübersicht')}", ""]
        files[knotenpfad(node)] = frontmatter(meta) + "\n".join(lines)
    files["graph.json"] = jsontext(dict(ontologie=schema["version"], **graph))
    files["log.md"] = "# Verarbeitungsstand\n\nDieser Stand ist reproduzierbar erzeugt. Das tatsächliche Ereignisprotokoll liegt in `protokolle/EREIGNISSE.jsonl`.\n\n" + f"- Ontologie: {schema['version']}\n- Quellen: {', '.join(graph['quellen'])}\n- Fachliche Freigabe: ausstehend\n- Vollständige Sprachmodell-Extraktion bei erneutem Aufruf: nein; die Demo verwendet gesicherte KI-Extraktionen.\n"
    return files


def ausgabe_pruefen(out):
    out = sicherer_pfad(out)
    rel = out.relative_to(ROOT)
    allowed = rel == Path("wiki") or (len(rel.parts) >= 4 and rel.parts[:2] == ("demo", "staende") and rel.parts[-1] == "wiki")
    if not allowed:
        raise GartenFehler("Ausgabe muss wiki oder demo/staende/<name>/wiki sein.")
    return out


def schreiben(out, files):
    marker = out / ".generiert.json"
    old = lesen(marker) if marker.exists() else {}
    # Prüfe vor dem ersten Schreibzugriff alle betroffenen Dateien.
    for name in set(old) | set(files):
        path = out / name
        if not path.exists():
            continue
        if name not in old or sha(path) != old[name]:
            raise GartenFehler(f"Manuell veränderte oder fremde Datei geschützt: {path.relative_to(ROOT)}")
    out.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for name in set(old) - set(files):
        (out / name).unlink(missing_ok=True)
    marker.write_text(jsontext({name: sha(out / name) for name in sorted(files)}), encoding="utf-8")


def bauen(phase, version, ausgabe, pakete=None, demo_freigabe=False):
    schema = schema_laden(version)
    if schema.get("freigabe") == "nur-demo" and not demo_freigabe:
        raise GartenFehler("Schema 1.1.0 braucht --demo-freigabe. Das bestätigt nur die simulierte Modellentscheidung der Demo.")
    manifest = lesen(ROOT / "raw/manifest.json")
    errors = quellen_pruefen(manifest)
    if errors:
        raise GartenFehler("\n".join(errors))
    paths = [sicherer_pfad(p) for p in pakete] if pakete else [ROOT / "extraktionen" / f"{q['id']}.json" for q in manifest if q["phase"] <= phase]
    graph = zusammenfuehren(paths, manifest)
    graph["eingaben"] = {
        "ontologie_sha256": sha(ROOT / "ontologie" / f"{version}.json"),
        "fragen_sha256": sha(ROOT / "ontologie/fragen.json"),
        "pakete": [{"pfad": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for path in paths],
    }
    errors = validieren(graph, schema, manifest)
    if errors:
        raise GartenFehler("Modell oder Extraktion nicht passend:\n" + "\n".join(errors))
    out = ausgabe_pruefen(ausgabe)
    files = rendern(graph, schema, manifest, out)
    schreiben(out, files)
    return graph


def links_pruefen(paths):
    errors = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?ms)^(`{3,}).*?^\1\s*$", "", text)
        for target in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", text):
            file, _, anchor = target.partition("#")
            dest = ROOT / file if file else path
            if not dest.suffix:
                dest = dest.with_suffix(".md")
            if not dest.exists():
                errors.append(f"{path.relative_to(ROOT)}: Linkziel fehlt: {target}")
            elif anchor and dest.suffix == ".md":
                headings = re.findall(r"(?m)^#{1,6} (.+)$", dest.read_text(encoding="utf-8"))
                if anchor not in headings:
                    errors.append(f"{path.relative_to(ROOT)}: Abschnitt fehlt: {target}")
        for target in re.findall(r"\]\(<([^>]+)>\)", text):
            local = target.split("#")[0]
            if "://" not in local and not (path.parent / local).exists():
                errors.append(f"{path.relative_to(ROOT)}: Dateilink fehlt: {target}")
    return errors


def pruefen(ausgabe="wiki"):
    out = ausgabe_pruefen(ausgabe)
    graph = lesen(out / "graph.json")
    manifest = lesen(ROOT / "raw/manifest.json")
    errors = quellen_pruefen(manifest) + validieren(graph, schema_laden(graph["ontologie"]), manifest)
    inputs = graph.get("eingaben", {})
    if inputs.get("ontologie_sha256") != sha(ROOT / "ontologie" / f"{graph['ontologie']}.json"):
        errors.append("Die Ontologiedatei wurde seit der Erzeugung verändert.")
    if inputs.get("fragen_sha256") != sha(ROOT / "ontologie/fragen.json"):
        errors.append("Die Kompetenzfragen wurden seit der Erzeugung verändert.")
    for packet in inputs.get("pakete", []):
        path = sicherer_pfad(packet["pfad"])
        if not path.is_file() or sha(path) != packet["sha256"]:
            errors.append(f"Extraktion seit der Erzeugung verändert: {packet['pfad']}")
    marker = lesen(out / ".generiert.json")
    for name, expected in marker.items():
        path = out / name
        if not path.is_file() or sha(path) != expected:
            errors.append(f"Erzeugte Datei fehlt oder wurde verändert: {name}")
    errors += links_pruefen(out.rglob("*.md"))
    return errors


def protokollieren(aktion, detail):
    path = ROOT / "protokolle/EREIGNISSE.jsonl"
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(zeit=datetime.now(timezone.utc).isoformat(timespec="seconds"), aktion=aktion,
                               detail=detail, akteur="KI/Programm; keine fachliche Freigabe"), ensure_ascii=False) + "\n")


def differenz(old, new, filename):
    lines = [f"# Änderungen: {filename}", "", "Automatisch aus den beiden Graphständen ermittelt.", ""]
    a, b = old["entitaeten"], new["entitaeten"]
    for title, ids in (("Neue Entitäten", set(b) - set(a)), ("Ergänzte Entitäten", {i for i in set(a) & set(b) if a[i] != b[i]})):
        lines += [f"## {title}", ""]
        lines += [f"- `{i}` · {b[i]['typ']} · {b[i]['titel']} · {len(b[i]['belege'])} Belege" for i in sorted(ids)] or ["Keine."]
        lines += [""]
    old_edges = {(e["von"], e["relation"], e["nach"]) for e in old["beziehungen"]}
    lines += ["## Neue Beziehungen", ""]
    lines += [f"- `{e['von']} → {e['relation']} → {e['nach']}`" for e in new["beziehungen"] if (e["von"], e["relation"], e["nach"]) not in old_edges]
    return "\n".join(lines) + "\n"


def demo():
    a = bauen(1, "1.0.0", "demo/staende/01-basis/wiki")
    b = bauen(2, "1.0.0", "demo/staende/02-neue-quelle/wiki")
    blocked = ROOT / "demo/staende/03-modellluecke/wiki"
    try:
        bauen(3, "1.0.0", blocked.relative_to(ROOT))
    except GartenFehler as exc:
        failure = str(exc)
    else:
        raise GartenFehler("Demo fehlgeschlagen: Q04 wurde unerwartet mit dem alten Modell angenommen.")
    if blocked.exists():
        raise GartenFehler("Bei der Modelllücke darf kein halbfertiges Wiki entstehen.")
    c = bauen(3, "1.1.0", "demo/staende/04-modell-erweitert/wiki", demo_freigabe=True)
    bauen(3, "1.1.0", "wiki", demo_freigabe=True)
    (ROOT / "demo/DIFF-01-02.md").write_text(differenz(a, b, "Neue Quelle; gleiches Modell"), encoding="utf-8")
    (ROOT / "demo/DIFF-02-04.md").write_text(differenz(b, c, "Neuer Begriff und neue Beziehungen"), encoding="utf-8")
    oldschema = (ROOT / "ontologie/1.0.0.json").read_text(encoding="utf-8").splitlines(True)
    newschema = (ROOT / "ontologie/1.1.0.json").read_text(encoding="utf-8").splitlines(True)
    (ROOT / "demo/ONTOLOGIE.diff").write_text("".join(difflib.unified_diff(oldschema, newschema, fromfile="1.0.0", tofile="1.1.0")), encoding="utf-8")
    (ROOT / "demo/ABGEWIESEN.md").write_text("# Q04 passt nicht in Ontologie 1.0.0\n\nDer Versuch wird vor dem Schreiben abgebrochen. Stand 02 bleibt unverändert.\n\n```text\n" + failure + "\n```\n\nEntscheidungsvorschlag: [[ontologie/AENDERUNG-001|Barrieren als eigenen Typ aufnehmen]].\n", encoding="utf-8")
    rows = []
    for label, directory in (("01 – Basis", "demo/staende/01-basis/wiki"), ("02 – Neue Quelle", "demo/staende/02-neue-quelle/wiki"),
                             ("04 – Modell erweitert", "demo/staende/04-modell-erweitert/wiki"), ("Aktueller Garten", "wiki")):
        errors = pruefen(directory)
        if errors:
            raise GartenFehler("\n".join(errors))
        graph = lesen(ROOT / directory / "graph.json")
        rows.append((label, graph["ontologie"], len(graph["quellen"]), len(graph["entitaeten"]), len(graph["beziehungen"])))
    report = ["# Prüfbericht der Demo", "", "Alle unten genannten Prüfungen wurden beim letzten Demo-Aufruf ausgeführt.", "",
              f"Prüfzeit: {datetime.now(timezone.utc).isoformat(timespec='seconds')}", "",
              "| Stand | Ontologie | Quellen | Entitäten | Beziehungen |", "|---|---|---:|---:|---:|"]
    report += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |" for r in rows]
    report += ["", "- Originale und Lesetexte stimmen mit den gespeicherten SHA-256-Prüfsummen überein.",
               "- Alle Belegkennungen, PDF-Seiten und Suchtexte sind prüfbar.", "- Alle Typen, Beziehungen und Pflichtfelder passen zum jeweiligen Schema.",
               "- Alle erzeugten Wiki-Links einschließlich Belegabschnitten haben ein Ziel.",
               "- Q04 wird mit dem alten Modell abgewiesen. Es entsteht kein Teil-Wiki.",
               "- Modell 1.1.0 wird nur mit ausdrücklich gesetzter Demo-Freigabe verwendet.",
               "- Die Prüfung bewertet keine inhaltliche Wahrheit und keine allgemeine Extraktionsqualität.", ""]
    (ROOT / "protokolle/DEMO-PRUEFBERICHT.md").write_text("\n".join(report), encoding="utf-8")
    protokollieren("demo", "Basis, neue Quelle, erwartete Ablehnung und simulierte Modellerweiterung erzeugt und technisch geprüft.")
    print("Demo vollständig. Drei Wiki-Stände und die erwartete Modelllücke sind geprüft. Start: demo/ABLAUF.md")


def main(argv=None):
    p = argparse.ArgumentParser(description="Knowledge Garden: Quellen, belegte Extraktionen und Markdown-Wiki.")
    sub = p.add_subparsers(dest="befehl", required=True)
    sub.add_parser("demo", help="Alle Demo-Stände offline erzeugen und prüfen")
    b = sub.add_parser("bauen", help="Extraktionen prüfen und Markdown erzeugen")
    b.add_argument("--phase", type=int, default=3)
    b.add_argument("--ontologie", default="1.0.0")
    b.add_argument("--ausgabe", default="wiki")
    b.add_argument("--pakete", nargs="+")
    b.add_argument("--demo-freigabe", action="store_true")
    c = sub.add_parser("pruefen", help="Quellen, Schema und Wiki-Links prüfen")
    c.add_argument("--wiki", default="wiki")
    c.add_argument("--alle-links", action="store_true")
    q = sub.add_parser("fragen", help="Eine feste Kompetenzfrage aus dem Graph beantworten")
    q.add_argument("kennung", help="KF01 bis KF07")
    q.add_argument("--wiki", default="wiki")
    r = sub.add_parser("registrieren", help="Neue lokale Quelle mit Herkunft unverändert sichern")
    for arg in ("id", "datei", "url", "titel", "herausgeber"):
        r.add_argument("--" + arg, required=True)
    r.add_argument("--jahr", default=None)
    r.add_argument("--phase", type=int, default=4)
    l = sub.add_parser("protokollieren", help="Tatsächlichen Arbeitsschritt unveränderlich anhängen")
    l.add_argument("aktion")
    l.add_argument("detail")
    args = p.parse_args(argv)
    try:
        if args.befehl == "demo":
            demo()
        elif args.befehl == "bauen":
            graph = bauen(args.phase, args.ontologie, args.ausgabe, args.pakete, args.demo_freigabe)
            protokollieren("bauen", f"{args.ausgabe}: Schema {args.ontologie}, Quellen {', '.join(graph['quellen'])}")
            print(f"Wiki erzeugt: {args.ausgabe}; {len(graph['entitaeten'])} Entitäten.")
        elif args.befehl == "pruefen":
            errors = pruefen(args.wiki)
            if args.alle_links:
                paths = [f for f in ROOT.rglob("*.md") if not any(x.startswith('.') for x in f.relative_to(ROOT).parts)]
                errors += links_pruefen(paths)
            if errors:
                raise GartenFehler("\n".join(errors))
            print("Prüfung erfolgreich. Quellen, Fundstellen, Modell und Links sind technisch konsistent.")
        elif args.befehl == "fragen":
            out = ausgabe_pruefen(args.wiki)
            graph = lesen(out / "graph.json")
            questions = {q["id"]: q for q in lesen(ROOT / "ontologie/fragen.json")}
            if args.kennung not in questions:
                raise GartenFehler("Unbekannte Kompetenzfrage. Nutze KF01 bis KF07. Freie Fragen bearbeitet der KI-Agent.")
            status, answer = frage_auswerten(questions[args.kennung], graph, schema_laden(graph["ontologie"]), out)
            print(questions[args.kennung]["frage"] + "\n\n" + answer)
            return 2 if status == "modellluecke" else 0
        elif args.befehl == "registrieren":
            registrieren(args)
        elif args.befehl == "protokollieren":
            protokollieren(args.aktion, args.detail)
    except (GartenFehler, OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"Abgebrochen: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
