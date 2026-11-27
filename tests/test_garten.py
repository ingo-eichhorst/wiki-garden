"""Prüft den echten Durchlauf und wichtige Fehlerfälle in einer isolierten Kopie."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("garten", Path(__file__).resolve().parents[1] / "skripte/garten.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
ORIGINAL = g.ROOT


class GartenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        for name in ("raw", "ontologie", "extraktionen"):
            shutil.copytree(ORIGINAL / name, self.root / name)
        g.ROOT = self.root
        self.manifest = g.lesen(self.root / "raw/manifest.json")
        self.schema = g.schema_laden("1.0.0")

    def tearDown(self):
        g.ROOT = ORIGINAL
        self.tmp.cleanup()

    def graph(self, phase=2):
        return g.zusammenfuehren([self.root / "extraktionen" / f"{q['id']}.json" for q in self.manifest if q["phase"] <= phase], self.manifest)

    def frage(self, ident, graph, schema=None):
        question = next(q for q in g.lesen(self.root / "ontologie/fragen.json") if q["id"] == ident)
        return g.frage_auswerten(question, graph, schema or self.schema, self.root / "wiki")

    def test_vollstaendiger_durchlauf_mit_erwarteter_modellluecke(self):
        a = g.bauen(1, "1.0.0", "demo/staende/01-basis/wiki")
        before = g.sha(self.root / "demo/staende/01-basis/wiki/graph.json")
        b = g.bauen(2, "1.0.0", "demo/staende/02-neue-quelle/wiki")
        self.assertEqual(a["quellen"], ["Q01", "Q02"])
        self.assertNotIn("P03", a["entitaeten"])
        self.assertIn("P03", b["entitaeten"])
        self.assertEqual(len(b["entitaeten"]["M01"]["belege"]), 3)
        self.assertEqual(self.frage("KF04", a)[0], "keine_belege")
        self.assertEqual(self.frage("KF04", b)[0], "beantwortet")
        with self.assertRaisesRegex(g.GartenFehler, "Unbekannter Typ Barriere"):
            g.bauen(3, "1.0.0", "demo/staende/03-modellluecke/wiki")
        self.assertFalse((self.root / "demo/staende/03-modellluecke/wiki").exists())
        c = g.bauen(3, "1.1.0", "wiki", demo_freigabe=True)
        self.assertEqual(g.validieren(c, g.schema_laden("1.1.0"), self.manifest), [])
        self.assertEqual(before, g.sha(self.root / "demo/staende/01-basis/wiki/graph.json"))
        self.assertEqual(b["entitaeten"]["E04"], c["entitaeten"]["E04"])
        self.assertIn("praezisiert", (self.root / "wiki/erkenntnisse/E04.md").read_text())
        self.assertEqual(self.frage("KF06", b)[0], "modellluecke")
        status, answer = self.frage("KF06", c, g.schema_laden("1.1.0"))
        self.assertEqual(status, "beantwortet")
        for expected in ("M05", "M06", "H01", "H02", "Q04:B01", "Q04:B02"):
            self.assertIn(expected, answer)

    def test_alle_sieben_kompetenzfragen_nach_erweiterung(self):
        graph = g.bauen(3, "1.1.0", "wiki", demo_freigabe=True)
        statuses = {}
        for q in g.lesen(self.root / "ontologie/fragen.json"):
            statuses[q["id"]] = self.frage(q["id"], graph, g.schema_laden("1.1.0"))[0]
        self.assertEqual(statuses, {f"KF0{i}": "beantwortet" if i <= 6 else "keine_belege" for i in range(1, 8)})
        self.assertIn("beweist keine Widerspruchsfreiheit", self.frage("KF07", graph)[1])

    def test_original_und_lesetext_sind_gesichert(self):
        self.assertEqual(g.quellen_pruefen(self.manifest), [])
        for key in ("original", "text", "lesetext"):
            path = self.root / self.manifest[0][key]
            old = path.read_bytes()
            path.write_bytes(old + b"\nveraendert")
            self.assertTrue(g.quellen_pruefen(self.manifest), key)
            path.write_bytes(old)

    def test_falscher_suchtext_wird_abgewiesen(self):
        graph = self.graph()
        graph["belege"]["Q01:B01"]["suchtext"] = "Dieser Text steht dort nicht."
        self.assertTrue(any("Suchtext" in e for e in g.validieren(graph, self.schema, self.manifest)))

    def test_falsche_pdf_seite_wird_abgewiesen(self):
        graph = self.graph()
        graph["belege"]["Q01:B01"]["seite"] = 999
        self.assertTrue(any("Ungültige PDF-Seite" in e for e in g.validieren(graph, self.schema, self.manifest)))

    def test_fehlender_beleg_und_unbekannte_kennung(self):
        graph = self.graph()
        graph["entitaeten"]["E01"]["belege"] = []
        graph["beziehungen"][0]["belege"] = ["Q99:B99"]
        errors = g.validieren(graph, self.schema, self.manifest)
        self.assertTrue(any("E01: Beleg fehlt" in e for e in errors))
        self.assertTrue(any("Unbekannter Beleg Q99:B99" in e for e in errors))

    def test_erkenntnis_braucht_kontext_und_evidenzgrenze(self):
        graph = self.graph()
        del graph["entitaeten"]["E01"]["grenzen"]
        graph["beziehungen"] = [e for e in graph["beziehungen"] if not (e["von"] == "E01" and e["relation"] == "gilt_im_kontext")]
        errors = g.validieren(graph, self.schema, self.manifest)
        self.assertTrue(any("Erkenntnisfeld fehlt: grenzen" in e for e in errors))
        self.assertTrue(any("Pflichtbeziehung fehlt: gilt_im_kontext" in e for e in errors))

    def test_falsche_beziehungstypen_und_fehlende_ziele(self):
        graph = self.graph()
        graph["beziehungen"][0]["nach"] = "K01"
        graph["beziehungen"][1]["nach"] = "X99"
        errors = g.validieren(graph, self.schema, self.manifest)
        self.assertTrue(any("unzulässige Typen" in e for e in errors))
        self.assertTrue(any("Ziel oder Ausgangspunkt fehlt" in e for e in errors))

    def test_identitaetskonflikt_verhindert_stilles_ueberschreiben(self):
        path = self.root / "extraktionen/Q02.json"
        packet = g.lesen(path)
        next(n for n in packet["entitaeten"] if n["id"] == "M01")["kurztext"] = "Andere Deutung"
        path.write_text(g.jsontext(packet))
        with self.assertRaisesRegex(g.GartenFehler, "Identitätskonflikt"):
            self.graph()

    def test_modellfreigabe_ist_ausdruecklich_nur_demo(self):
        with self.assertRaisesRegex(g.GartenFehler, "--demo-freigabe"):
            g.bauen(3, "1.1.0", "wiki")
        self.assertFalse((self.root / "wiki").exists())

    def test_manuelle_aenderungen_bleiben_erhalten(self):
        g.bauen(1, "1.0.0", "wiki")
        path = self.root / "wiki/erkenntnisse/E01.md"
        path.write_text("Manuelle Notiz\n")
        with self.assertRaisesRegex(g.GartenFehler, "Manuell veränderte"):
            g.bauen(2, "1.0.0", "wiki")
        self.assertEqual(path.read_text(), "Manuelle Notiz\n")
        self.assertFalse((self.root / "wiki/projekte/P03.md").exists())

    def test_wiederholung_aendert_keine_erzeugten_seiten(self):
        g.bauen(2, "1.0.0", "wiki")
        old = g.lesen(self.root / "wiki/.generiert.json")
        g.bauen(2, "1.0.0", "wiki")
        self.assertEqual(old, g.lesen(self.root / "wiki/.generiert.json"))

    def test_neue_textquelle_bis_zur_wikiseite(self):
        source = self.root / "neue-quelle.txt"
        source.write_text("Erfahrungsbericht\nEin Übungstreffen fand im Gemeindehaus statt.\n")
        args = argparse.Namespace(id="Q99", datei=str(source), titel="Neuer Erfahrungsbericht", herausgeber="Testquelle",
                                  url="https://example.org/testquelle", jahr="2026", phase=4)
        g.registrieren(args)
        packet = dict(quelle="Q99", status="fachlich-ungeprueft", belege=[dict(id="B01", abschnitt="Erfahrungsbericht",
                      suchtext="im Gemeindehaus", aussage="Der Ort war ein Gemeindehaus.")],
                      entitaeten=[dict(id="K99", typ="Kontext", titel="Lernen im Gemeindehaus", kurztext="Ein Angebot im Gemeindehaus.",
                                      belege=["Q99:B01"])], beziehungen=[])
        (self.root / "extraktionen/Q99.json").write_text(g.jsontext(packet))
        graph = g.bauen(4, "1.0.0", "wiki", pakete=["extraktionen/Q01.json", "extraktionen/Q02.json", "extraktionen/Q99.json"])
        self.assertIn("K99", graph["entitaeten"])
        self.assertTrue((self.root / "wiki/kontexte/K99.md").is_file())
        self.assertEqual(g.quellen_pruefen(g.lesen(self.root / "raw/manifest.json")), [])
        with self.assertRaisesRegex(g.GartenFehler, "bereits registriert"):
            g.registrieren(args)

    def test_veraenderte_eingaben_werden_erkannt(self):
        g.bauen(2, "1.0.0", "wiki")
        # Die globalen Navigationsziele gehören nicht zur isolierten Testkopie.
        for name in ("ONTOLOGY.md", "demo/ABLAUF.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Navigation\n")
        self.assertEqual(g.pruefen(), [])
        path = self.root / "extraktionen/Q01.json"
        path.write_text(path.read_text() + "\n")
        self.assertTrue(any("Extraktion seit der Erzeugung verändert" in e for e in g.pruefen()))

    def test_defekte_links_und_abschnitte_werden_erkannt(self):
        path = self.root / "test.md"
        path.write_text("[[fehlt|Kein Ziel]]\n[[test#Fehlt|Kein Abschnitt]]\n")
        errors = g.links_pruefen([path])
        self.assertEqual(len(errors), 2)

    def test_barrierenabfrage_beachtet_den_kontext(self):
        graph = self.graph(3)
        graph["entitaeten"]["H99"] = dict(id="H99", typ="Barriere", titel="Anderer Kontext")
        graph["beziehungen"].append(dict(von="M05", relation="adressiert", nach="H99", belege=["Q04:B01"]))
        status, answer = self.frage("KF06", graph, g.schema_laden("1.1.0"))
        self.assertEqual(status, "beantwortet")
        self.assertIn("H01", answer)
        self.assertNotIn("H99", answer)

    def test_ausgabe_darf_keine_quellen_ueberschreiben(self):
        for path in ("raw/originale", "ontologie", "../ausserhalb", ".obsidian"):
            with self.assertRaises(g.GartenFehler):
                g.ausgabe_pruefen(path)


if __name__ == "__main__":
    unittest.main()
