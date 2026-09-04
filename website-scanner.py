#!/usr/bin/env python3
"""website-scanner.py – Packungsscanner auf der Website ergänzen (DE + EN)."""
import pathlib, sys

ROOT = pathlib.Path(".")
de = ROOT / "index.html"
en = ROOT / "en" / "index.html"

assert de.exists(), f"{de} nicht gefunden – Skript im Webroot starten"
assert en.exists(), f"{en} nicht gefunden"

def patch(path, old, new, label=""):
    txt = path.read_text("utf-8")
    assert old in txt, f"ANKER NICHT GEFUNDEN ({label}): {old[:80]!r}"
    assert txt.count(old) == 1, f"ANKER MEHRDEUTIG ({label}): {old[:80]!r}"
    path.write_text(txt.replace(old, new), "utf-8")
    print(f"  ✓ {label}")

print("── DE ──")
patch(de,
    'Version 4.12 bringt Medikamente mit Einnahme-Erinnerungen — eingereicht und gerade in der App-Store-Freigabe; auf Android schon jetzt zum Download.',
    'Neu: Packungsscanner — Katheter und Medikamente per Kamera erkennen, Barcode scannen, eigenen Katalog aufbauen. Auf Android live, auf dem iPhone in Vorbereitung.',
    "Hero DE")
patch(de,
    'Urinfarbe, Bristol-Typ, Auffälligkeiten, Medikamente, Trinkmenge, Katheterbestand.</p>',
    'Urinfarbe, Bristol-Typ, Auffälligkeiten, Medikamente, Trinkmenge, Katheterbestand. Oder gleich die Packung scannen.</p>',
    "Schritt 2 DE")
patch(de,
    '<li><strong>Medikamente</strong><span>Anlegen, beim Eintrag antippen, an feste Einnahmezeiten erinnern lassen.</span></li>',
    '<li><strong>Medikamente</strong><span>Anlegen, beim Eintrag antippen, an feste Einnahmezeiten erinnern lassen.</span></li>\n          <li><strong>Packungsscanner</strong><span>Packung vor die Kamera halten — Barcode und Text werden erkannt, Name, Charrière und Material automatisch übernommen. Einmal gescannt, merkt sich die App die Packung fürs nächste Mal. Komplett offline.</span></li>',
    "Feature Packungsscanner DE")
patch(de,
    'Medikamente mit Einnahme-Erinnerungen,\n        Bristol-Skala',
    'Medikamente mit Einnahme-Erinnerungen, Packungsscanner für Katheter und Medikamente,\n        Bristol-Skala',
    "Android-Funktionssatz DE")

print("\n── EN ──")
patch(en,
    'Version 4.12 adds medications with intake reminders — submitted and currently in App Store review; already available for Android below.',
    'New: package scanner — recognise catheters and medications by camera, scan barcodes, build your own catalogue. Live on Android, coming to iPhone.',
    "Hero EN")
patch(en,
    'urine colour, Bristol type, signs, medications, fluid intake, catheter supply.</p>',
    'urine colour, Bristol type, signs, medications, fluid intake, catheter supply. Or just scan the package.</p>',
    "Step 2 EN")
patch(en,
    '<li><strong>Medications</strong><span>Set them up, tap them on an entry, get reminded at fixed intake times.</span></li>',
    '<li><strong>Medications</strong><span>Set them up, tap them on an entry, get reminded at fixed intake times.</span></li>\n          <li><strong>Package scanner</strong><span>Hold the package in front of the camera — barcode and text are recognised, name, Charrière and material filled in automatically. Once scanned, the app remembers the package for next time. Completely offline.</span></li>',
    "Feature Package scanner EN")
patch(en,
    'medications with intake reminders, the Bristol scale',
    'medications with intake reminders, package scanner for catheters and medications, the Bristol scale',
    "Android feature set EN")

print("\nFertig.")
