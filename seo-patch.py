#!/usr/bin/env python3
"""
SEO-Quick-Wins für blaseunddarm.de
===================================
Fügt auf allen 6 Wissensseiten (DE + EN) ein:
  1. JSON-LD Structured Data (MedicalWebPage + FAQPage)
  2. Autorenbox vor </main>
  3. Quellenabschnitt vor </main>
  4. SoftwareApplication-Schema auf den Startseiten
  5. robots.txt: Disallow /stats/ und /downloads/*.apk
  6. Alt-Text-Fix (vage "Statistik" → beschreibend)

Lauf: cd /var/www/blaseunddarm && python3 seo-patch.py
Danach: git add -A && git commit -m "SEO: Structured Data, Autorenbox, Quellen" && git push
"""

import re, os, sys, json
from pathlib import Path

ROOT = Path(__file__).parent
ERRORS = []

def must_exist(p):
    if not p.exists():
        ERRORS.append(f"FEHLT: {p}")
        return False
    return True

def patch_file(path, old, new, label=""):
    text = path.read_text("utf-8")
    if old not in text:
        ERRORS.append(f"Anker nicht gefunden in {path.name}: {label or old[:60]}")
        return False
    count = text.count(old)
    if count > 1:
        ERRORS.append(f"Anker {count}x in {path.name} — übersprungen: {label or old[:60]}")
        return False
    path.write_text(text.replace(old, new), "utf-8")
    return True

def insert_before(path, anchor, block, label=""):
    """Insert block BEFORE anchor in file."""
    text = path.read_text("utf-8")
    if anchor not in text:
        ERRORS.append(f"Anker nicht gefunden in {path.name}: {label or anchor[:60]}")
        return False
    if text.count(anchor) > 1:
        # Use first occurrence
        pass
    if block.strip()[:40] in text:
        print(f"  ⏭  {path.name}: {label or 'block'} bereits vorhanden")
        return True
    path.write_text(text.replace(anchor, block + "\n" + anchor, 1), "utf-8")
    return True

# ── 0. Preflight ──────────────────────────────────────────────

DE_PAGES = {
    "bristol.html": {
        "title_short": "Bristol-Skala: Stuhlformen Typ 1–7",
        "desc": "Die Bristol-Stuhlformen-Skala erklärt: was die sieben Typen über die Verdauung verraten und wann ein Arztbesuch ratsam ist.",
        "reviewed": "2026-08-19",
        "faq": [
            ("Was zeigt die Bristol-Skala?", "Die Bristol-Skala teilt Stuhlformen in sieben Typen ein — von harten Kügelchen (Typ 1) bis wässrigem Stuhl (Typ 7). Typ 3 und 4 gelten als normal."),
            ("Welcher Bristol-Typ ist normal?", "Typ 3 (wurstförmig mit Rissen) und Typ 4 (glatt und weich) gelten als Idealformen, die auf eine gesunde Verdauung hinweisen."),
        ],
        "sources_de": [
            ("Lewis SJ, Heaton KW: Stool form scale as a useful guide to intestinal transit time. <em>Scand J Gastroenterol</em>, 1997", "https://pubmed.ncbi.nlm.nih.gov/9299672/"),
        ],
    },
    "miktionsprotokoll.html": {
        "title_short": "Miktionsprotokoll (Blasentagebuch)",
        "desc": "Miktionsprotokoll richtig führen: was eingetragen wird, welche Werte als normal gelten und kostenlose PDF-Vorlage zum Ausdrucken.",
        "reviewed": "2026-08-19",
        "faq": [
            ("Was ist ein Miktionsprotokoll?", "Ein Miktionsprotokoll (Blasentagebuch) dokumentiert Trinkmengen, Toilettengänge und Urinmengen über mehrere Tage — die Grundlage für jede urologische Diagnose."),
            ("Wie lange muss ich ein Miktionsprotokoll führen?", "In der Regel zwei bis drei Tage, möglichst mit einem Wochentag und einem Wochenendtag. Bei ISK empfehlen Urologen oft zwei volle Wochen."),
        ],
        "sources_de": [
            ("S2k-Leitlinie: Neuro-urologische Versorgung querschnittgelähmter Patienten (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
        ],
    },
    "isk.html": {
        "title_short": "Intermittierender Selbstkatheterismus (ISK)",
        "desc": "ISK verständlich erklärt: warum katheterisiert wird, wie oft, welche Mengen, Kostenübernahme und Warnzeichen.",
        "reviewed": "2026-08-19",
        "faq": [
            ("Wie oft muss ich mich katheterisieren?", "In der Regel alle vier bis sechs Stunden, also vier- bis sechsmal am Tag. Die genaue Häufigkeit hängt von der Trinkmenge und der Blasenkapazität ab."),
            ("Wer übernimmt die Kosten für ISK-Katheter?", "Bei ärztlicher Verordnung übernimmt die gesetzliche Krankenkasse die Kosten für Einmalkatheter. Die Versorgung läuft über Hilfsmittelversorger wie PubliCare oder GHD."),
            ("Ist Selbstkatheterisieren schmerzhaft?", "Nein. Der ISK ist bei richtiger Technik und mit beschichteten Kathetern schmerzfrei. Am Anfang kann das Einführen ungewohnt sein, das legt sich mit Übung."),
        ],
        "sources_de": [
            ("S2k-Leitlinie: Neuro-urologische Versorgung querschnittgelähmter Patienten (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
            ("Wyndaele JJ et al.: Intermittent catheterisation with hydrophilic-coated catheters reduces the risk of clinical UTI. <em>Eur Urol</em>, 2012", "https://pubmed.ncbi.nlm.nih.gov/22633363/"),
        ],
    },
    "hwi.html": {
        "title_short": "Harnwegsinfekt bei neurogener Blase",
        "desc": "Harnwegsinfekt bei neurogener Blase und ISK erkennen: warum klassische Warnzeichen oft fehlen und wann es keinen Aufschub gibt.",
        "reviewed": "2026-08-19",
        "faq": [
            ("Wie erkenne ich einen Harnwegsinfekt beim ISK?", "Trüber oder stark riechender Urin, erhöhte Spastik, Abgeschlagenheit oder Fieber. Brennen fehlt bei neurogener Blase oft — deshalb auf andere Zeichen achten."),
            ("Muss jeder Bakteriennachweis im Urin behandelt werden?", "Nein. Eine asymptomatische Bakteriurie (Bakterien ohne Beschwerden) wird bei Katheternutzern in der Regel nicht mit Antibiotika behandelt, um Resistenzbildung zu vermeiden."),
        ],
        "sources_de": [
            ("S2k-Leitlinie: Neuro-urologische Versorgung querschnittgelähmter Patienten (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
            ("Harnwegsinfekte bei Querschnittlähmung (BG Klinikum Hamburg, 2017)", "https://www.bg-kliniken.de/fileadmin/01_hamburg/_content/PDFs/Harnwegsinfekte.pdf"),
        ],
    },
    "autonome-dysreflexie.html": {
        "title_short": "Autonome Dysreflexie",
        "desc": "Autonome Dysreflexie bei Querschnittlähmung ab Th6: Zeichen, häufigste Auslöser und Sofortmaßnahmen.",
        "reviewed": "2026-08-19",
        "faq": [
            ("Was ist autonome Dysreflexie?", "Eine akute Überreaktion des vegetativen Nervensystems bei Querschnittlähmung ab Höhe Th6, ausgelöst durch einen Reiz unterhalb der Lähmungshöhe — meist eine volle Blase. Sie kann zu einem lebensbedrohlichen Blutdruckanstieg führen."),
            ("Was tun bei autonomer Dysreflexie?", "Sofort aufrecht hinsetzen, beengende Kleidung öffnen, Blase entleeren (häufigster Auslöser). Blutdruck messen. Wenn die Symptome nicht nachlassen: Notarzt rufen."),
        ],
        "sources_de": [
            ("Krassioukov A et al.: Autonomic Dysreflexia Following Spinal Cord Injury. In: <em>Autonomic Failure</em>, Oxford, 2013", "https://pubmed.ncbi.nlm.nih.gov/"),
            ("Wallace E et al.: The Mystery of Autonomic Dysreflexia? NRH Ireland, 2013", ""),
        ],
    },
    "trinkmenge.html": {
        "title_short": "Trinkmenge bei ISK",
        "desc": "Trinkmenge bei ISK und neurogener Blase: warum weniger trinken der falsche Weg ist, welche Mengen sinnvoll sind und warum die Bilanz zählt.",
        "reviewed": "2026-08-19",
        "faq": [
            ("Wie viel sollte ich bei ISK trinken?", "In der Regel 1,5 bis 2 Liter am Tag, gleichmäßig über den Tag verteilt. Weniger trinken erhöht das Risiko für konzentrierten Urin und Harnwegsinfekte."),
            ("Warum ist weniger trinken bei ISK gefährlich?", "Konzentrierter Urin reizt die Blasenschleimhaut und fördert Bakterienwachstum. Die Folge: mehr Infekte, nicht weniger Katheterisierungen."),
        ],
        "sources_de": [
            ("S2k-Leitlinie: Neuro-urologische Versorgung querschnittgelähmter Patienten (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
        ],
    },
}

EN_PAGES = {
    "en/bristol.html": {
        "faq": [
            ("What does the Bristol Stool Scale show?", "The Bristol Stool Scale classifies stool into seven types — from hard lumps (Type 1) to entirely liquid (Type 7). Types 3 and 4 are considered normal."),
            ("Which Bristol type is normal?", "Type 3 (sausage-shaped with cracks) and Type 4 (smooth and soft) indicate healthy digestion."),
        ],
        "sources_en": [
            ("Lewis SJ, Heaton KW: Stool form scale as a useful guide to intestinal transit time. <em>Scand J Gastroenterol</em>, 1997", "https://pubmed.ncbi.nlm.nih.gov/9299672/"),
        ],
    },
    "en/bladder-diary.html": {
        "faq": [
            ("What is a bladder diary?", "A bladder diary records fluid intake, toilet visits and urine volumes over several days — the basis for any urological assessment."),
            ("How long should I keep a bladder diary?", "Usually two to three days. For intermittent catheterisation, urologists often recommend two full weeks."),
        ],
        "sources_en": [
            ("S2k Guideline: Neuro-urological care of patients with spinal cord injury (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
        ],
    },
    "en/intermittent-catheterisation.html": {
        "faq": [
            ("How often do I need to catheterise?", "Usually every four to six hours, i.e. four to six times a day. The exact frequency depends on fluid intake and bladder capacity."),
            ("Who covers the cost of ISC catheters?", "In Germany, statutory health insurance covers the cost of single-use catheters when prescribed by a doctor. Supply runs through specialist providers."),
            ("Is self-catheterisation painful?", "No. With proper technique and coated catheters, ISC is painless. Insertion may feel unusual at first but becomes routine with practice."),
        ],
        "sources_en": [
            ("S2k Guideline: Neuro-urological care of patients with spinal cord injury (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
            ("Wyndaele JJ et al.: Intermittent catheterisation with hydrophilic-coated catheters reduces the risk of clinical UTI. <em>Eur Urol</em>, 2012", "https://pubmed.ncbi.nlm.nih.gov/22633363/"),
        ],
    },
    "en/uti-neurogenic-bladder.html": {
        "faq": [
            ("How do I recognise a UTI with ISC?", "Cloudy or strong-smelling urine, increased spasticity, fatigue or fever. Burning is often absent with a neurogenic bladder — look for other signs instead."),
            ("Does every bacterium in the urine need treatment?", "No. Asymptomatic bacteriuria (bacteria without symptoms) is generally not treated with antibiotics in catheter users to avoid resistance."),
        ],
        "sources_en": [
            ("S2k Guideline: Neuro-urological care of patients with spinal cord injury (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
            ("UTIs in spinal cord injury (BG Klinikum Hamburg, 2017)", "https://www.bg-kliniken.de/fileadmin/01_hamburg/_content/PDFs/Harnwegsinfekte.pdf"),
        ],
    },
    "en/autonomic-dysreflexia.html": {
        "faq": [
            ("What is autonomic dysreflexia?", "An acute overreaction of the autonomic nervous system in spinal cord injuries at or above T6, triggered by a stimulus below the level of injury — most often a full bladder. It can cause a life-threatening spike in blood pressure."),
            ("What should I do during autonomic dysreflexia?", "Sit upright immediately, loosen tight clothing, empty the bladder (the most common trigger). Monitor blood pressure. If symptoms persist: call emergency services."),
        ],
        "sources_en": [
            ("Krassioukov A et al.: Autonomic Dysreflexia Following Spinal Cord Injury. In: <em>Autonomic Failure</em>, Oxford, 2013", "https://pubmed.ncbi.nlm.nih.gov/"),
        ],
    },
    "en/fluid-intake.html": {
        "faq": [
            ("How much should I drink with ISC?", "Usually 1.5 to 2 litres per day, spread evenly. Drinking less increases the risk of concentrated urine and urinary tract infections."),
            ("Why is drinking less dangerous with ISC?", "Concentrated urine irritates the bladder lining and promotes bacterial growth — leading to more infections, not fewer catheterisations."),
        ],
        "sources_en": [
            ("S2k Guideline: Neuro-urological care of patients with spinal cord injury (AWMF 179-001, 2021)", "https://register.awmf.org/de/leitlinien/detail/179-001"),
        ],
    },
}

# ── 1. Structured Data — JSON-LD for knowledge pages ──────────

def build_jsonld_medical(title, desc, url, reviewed, faq_pairs):
    """Build MedicalWebPage + FAQPage JSON-LD."""
    medical = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": title,
        "description": desc,
        "url": url,
        "lastReviewed": reviewed,
        "author": {
            "@type": "Person",
            "name": "André Bajorat",
            "url": "https://blaseunddarm.de/ueber-mich.html",
            "description": "Querschnittgelähmt, ISK-Anwender, Entwickler der Blase & Darm Manager App"
        },
        "publisher": {
            "@type": "Organization",
            "name": "blaseunddarm.de",
            "url": "https://blaseunddarm.de/"
        },
        "inLanguage": "de" if "/en/" not in url else "en"
    }

    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a
                }
            }
            for q, a in faq_pairs
        ]
    }

    return (
        '<script type="application/ld+json">\n'
        + json.dumps(medical, ensure_ascii=False, indent=2)
        + '\n</script>\n'
        '<script type="application/ld+json">\n'
        + json.dumps(faq, ensure_ascii=False, indent=2)
        + '\n</script>'
    )


def build_jsonld_app():
    """SoftwareApplication schema for the index pages."""
    app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Blase & Darm Manager",
        "operatingSystem": "iOS 17+, Android 8+",
        "applicationCategory": "HealthApplication",
        "description": "Miktionsprotokoll-App für intermittierenden Selbstkatheterismus (ISK) und neurogene Blasenfunktionsstörung.",
        "url": "https://blaseunddarm.de/",
        "downloadUrl": "https://apps.apple.com/de/app/blase-darm-manager/id6792282103",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "EUR"
        },
        "author": {
            "@type": "Person",
            "name": "André Bajorat"
        }
    }
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(app, ensure_ascii=False, indent=2)
        + '\n</script>'
    )


# ── 2. Author box + Sources ──────────────────────────────────

AUTHOR_DE = """
  <section class="section wrap" style="margin-top:3rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Über den Autor</h2>
      <p style="font-size:.95rem">
        André Bajorat ist querschnittgelähmt und katheterisiert sich seit 2025 selbst.
        Er hat die App <a href="/">Blase &amp; Darm Manager</a> entwickelt und schreibt auf
        <a href="https://ploetzlich-querschnitt.de" rel="noopener">plötzlich querschnitt</a>
        über das Leben mit Querschnittlähmung. Mehr auf der <a href="/ueber-mich.html">Über-mich-Seite</a>.
      </p>
      <p style="font-size:.85rem;color:var(--ink-soft);margin-top:.5rem">
        Medizinische Grundlage: <a href="https://register.awmf.org/de/leitlinien/detail/179-001" rel="noopener nofollow" style="color:inherit">S2k-Leitlinie Neuro-urologische Versorgung querschnittgelähmter Patienten (AWMF, 2021)</a>.
        Diese Seite ersetzt keine ärztliche Beratung.
      </p>
    </div>
  </section>
"""

AUTHOR_EN = """
  <section class="section wrap" style="margin-top:3rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">About the author</h2>
      <p style="font-size:.95rem">
        André Bajorat has a spinal cord injury and has been self-catheterising since 2025.
        He built the <a href="/en/">Bladder &amp; Bowel Manager</a> app and writes about
        life with a spinal cord injury at
        <a href="https://ploetzlich-querschnitt.de" rel="noopener">plötzlich querschnitt</a>.
        More on the <a href="/en/about.html">about page</a>.
      </p>
      <p style="font-size:.85rem;color:var(--ink-soft);margin-top:.5rem">
        Medical basis: <a href="https://register.awmf.org/de/leitlinien/detail/179-001" rel="noopener nofollow" style="color:inherit">S2k guideline on neuro-urological care of spinal cord injury patients (AWMF, 2021)</a>.
        This page does not replace medical advice.
      </p>
    </div>
  </section>
"""

def build_sources_de(sources):
    if not sources:
        return ""
    items = "\n".join(
        f'      <li>{text}' + (f' <a href="{url}" rel="noopener nofollow" style="color:inherit">↗</a>' if url else '') + '</li>'
        for text, url in sources
    )
    return f"""
  <section class="section wrap" style="margin-top:1rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Quellen</h2>
      <ol style="font-size:.85rem;color:var(--ink-soft);padding-left:1.5rem">
{items}
      </ol>
    </div>
  </section>
"""

def build_sources_en(sources):
    if not sources:
        return ""
    items = "\n".join(
        f'      <li>{text}' + (f' <a href="{url}" rel="noopener nofollow" style="color:inherit">↗</a>' if url else '') + '</li>'
        for text, url in sources
    )
    return f"""
  <section class="section wrap" style="margin-top:1rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Sources</h2>
      <ol style="font-size:.85rem;color:var(--ink-soft);padding-left:1.5rem">
{items}
      </ol>
    </div>
  </section>
"""


# ── 3. Patch all pages ────────────────────────────────────────

def get_canonical(path):
    text = Path(path).read_text("utf-8")
    m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    return m.group(1) if m else ""

def run():
    os.chdir(ROOT)

    changed = 0

    # ── DE knowledge pages ──
    for filename, data in DE_PAGES.items():
        p = ROOT / filename
        if not must_exist(p):
            continue

        url = get_canonical(p)
        print(f"\n✏️  {filename}")

        # 1. JSON-LD in <head>
        if "application/ld+json" not in p.read_text("utf-8"):
            jsonld = build_jsonld_medical(
                data["title_short"], data["desc"], url,
                data["reviewed"], data["faq"]
            )
            ok = insert_before(p, '</head>', jsonld, "JSON-LD")
            if ok:
                print(f"  ✅ JSON-LD eingefügt")
                changed += 1
        else:
            print(f"  ⏭  JSON-LD bereits vorhanden")

        # 2. Author box + Sources before </main>
        if "Über den Autor" not in p.read_text("utf-8"):
            sources_block = build_sources_de(data.get("sources_de", []))
            block = sources_block + AUTHOR_DE
            ok = insert_before(p, '</main>', block, "Autorenbox+Quellen")
            if ok:
                print(f"  ✅ Autorenbox + Quellen eingefügt")
                changed += 1
        else:
            print(f"  ⏭  Autorenbox bereits vorhanden")

    # ── EN knowledge pages ──
    for filename, data in EN_PAGES.items():
        p = ROOT / filename
        if not must_exist(p):
            continue

        url = get_canonical(p)
        print(f"\n✏️  {filename}")

        # 1. JSON-LD
        if "application/ld+json" not in p.read_text("utf-8"):
            # Derive title/desc from existing <title> and <meta description>
            text = p.read_text("utf-8")
            m_title = re.search(r'<title>([^<]+)</title>', text)
            m_desc = re.search(r'<meta name="description" content="([^"]+)"', text)
            title = m_title.group(1) if m_title else filename
            desc = m_desc.group(1) if m_desc else ""
            reviewed = "2026-08-19"

            jsonld = build_jsonld_medical(title, desc, url, reviewed, data["faq"])
            ok = insert_before(p, '</head>', jsonld, "JSON-LD")
            if ok:
                print(f"  ✅ JSON-LD eingefügt")
                changed += 1
        else:
            print(f"  ⏭  JSON-LD bereits vorhanden")

        # 2. Author box + Sources
        if "About the author" not in p.read_text("utf-8"):
            sources_block = build_sources_en(data.get("sources_en", []))
            block = sources_block + AUTHOR_EN
            ok = insert_before(p, '</main>', block, "Author+Sources")
            if ok:
                print(f"  ✅ Author box + Sources eingefügt")
                changed += 1
        else:
            print(f"  ⏭  Author box bereits vorhanden")

    # ── Index pages: SoftwareApplication schema ──
    for idx_file in ["index.html", "en/index.html"]:
        p = ROOT / idx_file
        if not must_exist(p):
            continue
        print(f"\n✏️  {idx_file}")
        if "application/ld+json" not in p.read_text("utf-8"):
            ok = insert_before(p, '</head>', build_jsonld_app(), "App-Schema")
            if ok:
                print(f"  ✅ SoftwareApplication JSON-LD eingefügt")
                changed += 1
        else:
            print(f"  ⏭  JSON-LD bereits vorhanden")

    # ── robots.txt ──
    print(f"\n✏️  robots.txt")
    robots = ROOT / "robots.txt"
    rt = robots.read_text("utf-8")
    if "Disallow: /stats/" not in rt:
        new_rt = rt.replace(
            "Allow: /",
            "Allow: /\nDisallow: /stats/\nDisallow: /downloads/*.apk"
        )
        robots.write_text(new_rt, "utf-8")
        print(f"  ✅ Disallow /stats/ und /downloads/*.apk ergänzt")
        changed += 1
    else:
        print(f"  ⏭  robots.txt bereits gepatcht")

    # ── Alt-text fixes ──
    print(f"\n✏️  Alt-Text-Fixes")
    for idx_file in ["index.html", "en/index.html"]:
        p = ROOT / idx_file
        text = p.read_text("utf-8")
        old_alt = 'alt="Statistik"'
        new_alt_de = 'alt="Statistik-Ansicht mit Katheterbestand, Darm-Karte und Auffälligkeiten"'
        new_alt_en = 'alt="Statistics view with catheter stock, bowel card and symptom patterns"'
        new_alt = new_alt_de if "en/" not in idx_file else new_alt_en
        if old_alt in text:
            text = text.replace(old_alt, new_alt, 1)
            p.write_text(text, "utf-8")
            print(f"  ✅ {idx_file}: Alt-Text verbessert")
            changed += 1
        else:
            print(f"  ⏭  {idx_file}: kein vager Alt-Text gefunden")

    # ── Summary ──
    print(f"\n{'='*50}")
    print(f"✅ {changed} Änderungen vorgenommen")
    if ERRORS:
        print(f"\n⚠️  {len(ERRORS)} Probleme:")
        for e in ERRORS:
            print(f"   • {e}")
    else:
        print("Keine Fehler.")

    print(f"\nNächster Schritt auf dem VPS:")
    print(f"  cd /var/www/blaseunddarm")
    print(f"  python3 seo-patch.py")
    print(f'  git add -A && git commit -m "SEO: Structured Data, Autorenbox, Quellen, robots.txt" && git push')


if __name__ == "__main__":
    run()
