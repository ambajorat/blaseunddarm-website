#!/usr/bin/env python3
"""
SEO Runde 2: Neue Seiten + Sitemap
====================================
1. urinfarbe.html (DE) + en/urine-colour.html (EN)
2. wissen.html (DE) + en/knowledge.html (EN) — Pillar-Seite
3. sitemap.xml ergänzen
4. Footer-Navigation um Urinfarbe erweitern
5. Internal Links auf bestehenden Seiten ergänzen

Lauf: cd /var/www/blaseunddarm && python3 seo-seiten.py
Danach: git add -A && git commit -m "SEO: Urinfarbe + Wissen-Pillar + Sitemap" && git push
"""

import os, json, re
from pathlib import Path

ROOT = Path(__file__).parent
ERRORS = []

def safe_write(path, content):
    path.write_text(content, "utf-8")
    print(f"  ✅ {path.relative_to(ROOT)} geschrieben")

def patch_file(path, old, new, label=""):
    text = path.read_text("utf-8")
    if old not in text:
        ERRORS.append(f"Anker nicht gefunden in {path.name}: {label or old[:60]}")
        return False
    if new in text:
        print(f"  ⏭  {path.name}: {label} bereits vorhanden")
        return True
    path.write_text(text.replace(old, new, 1), "utf-8")
    print(f"  ✅ {path.name}: {label}")
    return True

# ── Shared fragments ──

MASTHEAD_DE = """<header class="masthead">
  <div class="wrap masthead__inner">
    <a class="wordmark" href="/"><span class="wordmark__dots"><i></i><i></i></span> Blase &amp; Darm Manager</a>
    <nav aria-label="Hauptnavigation">
      <a href="/#funktionen">Funktionen</a>
      <a href="/wissen.html">Wissen</a>
      <a href="/ueber-mich.html">Über mich</a>
      <a href="/support.html">Support</a>
      <a class="lang" href="{en_href}" hreflang="en" lang="en">EN</a>
    </nav>
  </div>
</header>"""

MASTHEAD_EN = """<header class="masthead">
  <div class="wrap masthead__inner">
    <a class="wordmark" href="/en/"><span class="wordmark__dots"><i></i><i></i></span> Bladder &amp; Bowel Manager</a>
    <nav aria-label="Main navigation">
      <a href="/en/#features">Features</a>
      <a href="/en/knowledge.html">Knowledge</a>
      <a href="/en/about.html">About</a>
      <a href="/en/support.html">Support</a>
      <a class="lang" href="{de_href}" hreflang="de" lang="de">DE</a>
    </nav>
  </div>
</header>"""

FOOTER_DE = """<footer class="foot">
  <div class="wrap">
    <div class="foot__inner">
      <span>© <span id="jahr">2026</span> Blase &amp; Darm Manager</span>
      <nav aria-label="Rechtliches">
        <a href="https://ploetzlich-querschnitt.de">plötzlich querschnitt</a>
        <a href="/">Start</a>
        <a href="/wissen.html">Wissen</a>
        <a href="/bristol.html">Bristol-Skala</a>
        <a href="/miktionsprotokoll.html">Miktionsprotokoll</a>
        <a href="/isk.html">ISK</a>
        <a href="/hwi.html">Harnwegsinfekt</a>
        <a href="/autonome-dysreflexie.html">Dysreflexie</a>
        <a href="/trinkmenge.html">Trinkmenge</a>
        <a href="/urinfarbe.html">Urinfarbe</a>
        <a href="/support.html">Support</a>
        <a href="/datenschutz.html">Datenschutz</a>
        <a href="/impressum.html">Impressum</a>
        <a href="{en_href}" hreflang="en" lang="en">English</a>
      </nav>
    </div>
    <p class="disclaimer">
      Diese Seite dient der allgemeinen Information und ersetzt keine ärztliche Beratung,
      Diagnose oder Behandlung. Bei Beschwerden ärztlichen Rat einholen.
    </p>
    <p class="marken">Apple, das Apple-Logo, iPhone, iPad, Apple Watch, Siri und CarPlay sind Marken von Apple Inc., eingetragen in den USA und anderen Ländern. App Store und TestFlight sind Dienstleistungsmarken von Apple Inc. Diese Website steht in keiner Verbindung zu Apple Inc.</p>
    <p><a class="nach-oben" href="#main">↑ Nach oben</a></p>
  </div>
</footer>

<script>document.getElementById('jahr').textContent = new Date().getFullYear();</script>
</body>
</html>"""

FOOTER_EN = """<footer class="foot">
  <div class="wrap">
    <div class="foot__inner">
      <span>© <span id="jahr">2026</span> Bladder &amp; Bowel Manager</span>
      <nav aria-label="Legal">
        <a href="https://ploetzlich-querschnitt.de">plötzlich querschnitt</a>
        <a href="/en/">Home</a>
        <a href="/en/knowledge.html">Knowledge</a>
        <a href="/en/bristol.html">Bristol Scale</a>
        <a href="/en/bladder-diary.html">Bladder Diary</a>
        <a href="/en/intermittent-catheterisation.html">ISC</a>
        <a href="/en/uti-neurogenic-bladder.html">UTI</a>
        <a href="/en/autonomic-dysreflexia.html">Dysreflexia</a>
        <a href="/en/fluid-intake.html">Fluid Intake</a>
        <a href="/en/urine-colour.html">Urine Colour</a>
        <a href="/en/support.html">Support</a>
        <a href="/en/privacy.html">Privacy</a>
        <a href="/en/imprint.html">Imprint</a>
        <a href="{de_href}" hreflang="de" lang="de">Deutsch</a>
      </nav>
    </div>
    <p class="disclaimer">
      This page is for general information only and does not replace medical advice,
      diagnosis or treatment. Seek medical advice if you have concerns.
    </p>
    <p class="marken">Apple, the Apple logo, iPhone, iPad, Apple Watch, Siri and CarPlay are trademarks of Apple Inc., registered in the U.S. and other countries. App Store and TestFlight are service marks of Apple Inc. This website is not affiliated with Apple Inc.</p>
    <p><a class="nach-oben" href="#main">↑ To the top</a></p>
  </div>
</footer>

<script>document.getElementById('jahr').textContent = new Date().getFullYear();</script>
</body>
</html>"""

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

# ── 1. Urinfarbe (DE) ────────────────────────────────────────

URINFARBE_DE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Urinfarbe: was die Farbe über Blase und Gesundheit verrät</title>
<meta name="description" content="Urinfarbe von klar bis dunkelbraun: was jede Farbe bedeutet, wann es harmlos ist und welche Veränderungen ärztlich abgeklärt werden sollten — besonders bei ISK und neurogener Blase.">
<link rel="canonical" href="https://blaseunddarm.de/urinfarbe.html">
<link rel="alternate" hreflang="de" href="https://blaseunddarm.de/urinfarbe.html">
<link rel="alternate" hreflang="en" href="https://blaseunddarm.de/en/urine-colour.html">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="Urinfarbe: was die Farbe über Blase und Gesundheit verrät">
<meta property="og:description" content="Was jede Urinfarbe bedeutet — besonders bei ISK und neurogener Blase.">
<meta property="og:type" content="article">
<meta property="og:url" content="https://blaseunddarm.de/urinfarbe.html">
<meta property="og:locale" content="de_DE">
<link rel="stylesheet" href="/assets/style.css">
<style>
  .lede { font-size: clamp(1.05rem, 1rem + 0.4vw, 1.35rem); color: var(--ink-soft); max-width: 48ch; margin: 0 0 2rem; }
  .farbe { display: grid; grid-template-columns: 3rem 1fr; gap: 1.25rem; align-items: start; padding: 1.5rem 0; border-bottom: 1px solid var(--line-soft); }
  .farbe:first-of-type { border-top: 1px solid var(--line); }
  .farbe__dot { width: 2.4rem; height: 2.4rem; border-radius: 50%; margin-top: .2rem; border: 1px solid var(--line-soft); }
  .farbe h3 { margin: 0 0 .3rem; font-size: 1.05rem; }
  .farbe p { margin: 0; font-size: .95rem; color: var(--ink-soft); }
  .hinweis { border-left: 3px solid var(--blase); background: var(--surface); padding: 1.25rem 1.5rem; margin: 2rem 0; font-size: 0.95rem; }
  .hinweis p { margin: 0; color: var(--ink-soft); }
  .hinweis strong { color: var(--ink); }
</style>
<link rel="stylesheet" href="/assets/fonts.css?v=1">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalWebPage",
  "name": "Urinfarbe: Bedeutung und Warnzeichen",
  "description": "Was jede Urinfarbe bedeutet, wann es harmlos ist und welche Veränderungen bei ISK und neurogener Blase ärztlich abgeklärt werden sollten.",
  "url": "https://blaseunddarm.de/urinfarbe.html",
  "lastReviewed": "2026-09-05",
  "author": {
    "@type": "Person",
    "name": "André Bajorat",
    "url": "https://blaseunddarm.de/ueber-mich.html",
    "description": "Querschnittgelähmt, ISK-Anwender, Entwickler der Blase & Darm Manager App"
  },
  "publisher": { "@type": "Organization", "name": "blaseunddarm.de", "url": "https://blaseunddarm.de/" },
  "inLanguage": "de"
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "Was bedeutet trüber Urin?", "acceptedAnswer": { "@type": "Answer", "text": "Trüber Urin kann auf einen Harnwegsinfekt hinweisen — besonders bei ISK und neurogener Blase. Wenn Trübung über mehr als einen Tag anhält oder von Geruch, Fieber oder Spastik begleitet wird, sollte der Urin ärztlich untersucht werden." } },
    { "@type": "Question", "name": "Welche Urinfarbe ist normal?", "acceptedAnswer": { "@type": "Answer", "text": "Hellgelb bis strohgelb. Sehr blasser Urin deutet auf hohe Trinkmenge hin, dunkelgelber auf zu wenig Flüssigkeit." } },
    { "@type": "Question", "name": "Wann ist rötlicher Urin ein Notfall?", "acceptedAnswer": { "@type": "Answer", "text": "Einzelne rosa Tropfen nach dem Katheterisieren können von einer kleinen Schleimhautirritation stammen. Anhaltend rötlicher oder brauner Urin sollte zeitnah ärztlich abgeklärt werden — vor allem in Verbindung mit Schmerzen oder Fieber." } }
  ]
}
</script>
</head>
<body>
<a class="skip" href="#main">Zum Inhalt springen</a>

""" + MASTHEAD_DE.format(en_href="/en/urine-colour.html") + r"""

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Nachschlagen</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">
      Was die Farbe im Beutel erzählt.
    </h1>
    <p class="lede">
      Wer regelmäßig katheterisiert, sieht seinen Urin bei jedem Mal. Das ist ein Vorteil:
      Veränderungen fallen früh auf. Diese Seite zeigt, was die Farben bedeuten — und wann
      es sich lohnt, genauer hinzuschauen.
    </p>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Die Farben im Überblick</h2>

      <div class="farbe">
        <div class="farbe__dot" style="background:#f0f0e8"></div>
        <div>
          <h3>Fast farblos</h3>
          <p>Sehr hohe Trinkmenge. Beim ISK in Ordnung, solange die Einzelmengen pro
            Katheterisierung nicht über 400–500 ml liegen. Bei Herz- oder Nierenerkrankung
            mit dem Arzt besprechen.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background:#f5e6a0"></div>
        <div>
          <h3>Hellgelb / Strohgelb</h3>
          <p>Normal. Der Farbstoff Urochrom ist ausreichend verdünnt. Die Trinkmenge passt.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background:#e0b830"></div>
        <div>
          <h3>Dunkelgelb / Bernstein</h3>
          <p>Zu wenig getrunken. Konzentrierter Urin reizt die Blasenschleimhaut und
            begünstigt Harnwegsinfekte. Mehr trinken — die
            <a href="/trinkmenge.html">Trinkmenge-Seite</a> erklärt, wie viel.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background:#c8b898; opacity:.7"></div>
        <div>
          <h3>Trüb / Milchig</h3>
          <p>Häufig ein Hinweis auf einen <a href="/hwi.html">Harnwegsinfekt</a>, vor allem
            wenn Geruch, Fieber oder erhöhte Spastik dazukommen. Einzelne Trübungen können
            auch von Schleim oder Sediment stammen — hält es länger als einen Tag an, Urin
            untersuchen lassen.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background:#e8a0a0"></div>
        <div>
          <h3>Rosa / Leicht rötlich</h3>
          <p>Einzelne rosa Tropfen nach dem Katheterisieren können von einer kleinen
            Schleimhautirritation stammen — besonders bei trockenen oder zu großen
            Kathetern. Wenn es sich wiederholt oder mehr wird: ärztlich abklären.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background:#b04040"></div>
        <div>
          <h3>Rot / Braun</h3>
          <p>Blut im Urin (Hämaturie). Kann von einer Infektion, einem Stein oder einer
            Verletzung stammen. Zeitnah ärztlich abklären lassen — vor allem in Verbindung
            mit Schmerzen, Fieber oder bei Querschnittlähmung ab Th6 mit Zeichen einer
            <a href="/autonome-dysreflexie.html">autonomen Dysreflexie</a>.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background:#d08020"></div>
        <div>
          <h3>Orange</h3>
          <p>Kann von Medikamenten (z. B. Phenazopyridin), B-Vitaminen oder starker
            Konzentration kommen. Wenn kein Medikament die Ursache erklärt: ärztlich prüfen
            lassen.</p>
        </div>
      </div>

      <div class="farbe">
        <div class="farbe__dot" style="background: linear-gradient(135deg, #80a860 40%, #607840)"></div>
        <div>
          <h3>Grünlich</h3>
          <p>Selten. Kann von bestimmten Bakterien (Pseudomonas), Medikamenten oder
            Lebensmittelfarbstoffen stammen. Ärztlich abklären.</p>
        </div>
      </div>

    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Warum Urinfarbe beim ISK besonders wichtig ist</h2>
      <p>
        Bei neurogener Blase fehlen die üblichen Warnsignale: kein Brennen, kein bewusster
        Harndrang, oft auch kein Schmerzempfinden. Was bleibt, ist das, was man sieht — Farbe,
        Trübung, Geruch. Wer diese Zeichen bei jedem Katheterisieren kurz registriert, bemerkt
        einen Infekt oder eine andere Veränderung früher als mit jedem Labortest.
      </p>
      <p>
        In der App <a href="/">Blase &amp; Darm Manager</a> lässt sich die Urinfarbe bei
        jedem Eintrag mit einem Tipp erfassen. Anhaltend trüber Urin löst einen Hinweis aus.
        Zusammen mit den <a href="/hwi.html">HWI-Auffälligkeiten</a> ergibt sich ein Bild,
        das beim nächsten Arzttermin mehr sagt als die Erinnerung.
      </p>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Wann es keinen Aufschub gibt</h2>

      <div class="hinweis">
        <p>
          <strong>Sofort ärztlich abklären:</strong> Anhaltend rötlicher oder brauner Urin,
          Fieber mit Flankenschmerzen, Urin mit starkem oder ungewöhnlichem Geruch zusammen
          mit Abgeschlagenheit oder Spastik. Bei Querschnittlähmung ab Th6: pochender
          Kopfschmerz und Schwitzen oberhalb der Lähmungshöhe —
          <a href="/autonome-dysreflexie.html">Zeichen einer autonomen Dysreflexie</a>.
        </p>
      </div>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Warum mitschreiben hilft</h2>
      <p>
        „Seit wann ist der Urin trüb?" — die Frage kommt bei jedem Arzttermin. Mit einem
        kurzen Farbvermerk bei jedem Katheterisieren lässt sie sich beantworten, ohne raten
        zu müssen. Auf Papier geht das mit der
        <a href="/miktionsprotokoll.html">Miktionsprotokoll-Vorlage</a>. Bequemer ist der
        <a href="/">Blase &amp; Darm Manager</a>: Farbe und Auffälligkeiten als Ein-Tipp-Chips,
        Hinweise bei Mustern und ein PDF-Bericht für den nächsten Termin. Alles bleibt auf dem Gerät.
      </p>
    </div>
    <div class="actions" style="margin-top:2.5rem">
      <a class="btn btn--ghost" href="/isk.html">Zur ISK-Seite</a>
      <a class="btn btn--ghost" href="/hwi.html">HWI erkennen</a>
      <a class="btn btn--ghost" href="/">Zur App</a>
    </div>
  </section>

  <section class="section wrap" style="margin-top:1rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Quellen</h2>
      <ol style="font-size:.85rem;color:var(--ink-soft);padding-left:1.5rem">
        <li>S2k-Leitlinie: Neuro-urologische Versorgung querschnittgelähmter Patienten (AWMF 179-001, 2021) <a href="https://register.awmf.org/de/leitlinien/detail/179-001" rel="noopener nofollow" style="color:inherit">↗</a></li>
        <li>Simerville JA et al.: Urinalysis: A Comprehensive Review. <em>Am Fam Physician</em>, 2005 <a href="https://pubmed.ncbi.nlm.nih.gov/15791892/" rel="noopener nofollow" style="color:inherit">↗</a></li>
      </ol>
    </div>
  </section>
""" + AUTHOR_DE + r"""
</main>

""" + FOOTER_DE.format(en_href="/en/urine-colour.html")


# ── 2. Urine Colour (EN) ─────────────────────────────────────

URINFARBE_EN = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Urine colour: what the colour tells you about bladder health</title>
<meta name="description" content="Urine colour from clear to dark brown: what each shade means, when it is harmless and which changes should be checked — especially with ISC and a neurogenic bladder.">
<link rel="canonical" href="https://blaseunddarm.de/en/urine-colour.html">
<link rel="alternate" hreflang="en" href="https://blaseunddarm.de/en/urine-colour.html">
<link rel="alternate" hreflang="de" href="https://blaseunddarm.de/urinfarbe.html">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="Urine colour: what it tells you about bladder health">
<meta property="og:description" content="What each urine colour means — especially with ISC and a neurogenic bladder.">
<meta property="og:type" content="article">
<meta property="og:url" content="https://blaseunddarm.de/en/urine-colour.html">
<meta property="og:locale" content="en_GB">
<link rel="stylesheet" href="/assets/style.css">
<style>
  .lede { font-size: clamp(1.05rem, 1rem + 0.4vw, 1.35rem); color: var(--ink-soft); max-width: 48ch; margin: 0 0 2rem; }
  .farbe { display: grid; grid-template-columns: 3rem 1fr; gap: 1.25rem; align-items: start; padding: 1.5rem 0; border-bottom: 1px solid var(--line-soft); }
  .farbe:first-of-type { border-top: 1px solid var(--line); }
  .farbe__dot { width: 2.4rem; height: 2.4rem; border-radius: 50%; margin-top: .2rem; border: 1px solid var(--line-soft); }
  .farbe h3 { margin: 0 0 .3rem; font-size: 1.05rem; }
  .farbe p { margin: 0; font-size: .95rem; color: var(--ink-soft); }
  .hinweis { border-left: 3px solid var(--blase); background: var(--surface); padding: 1.25rem 1.5rem; margin: 2rem 0; font-size: 0.95rem; }
  .hinweis p { margin: 0; color: var(--ink-soft); }
  .hinweis strong { color: var(--ink); }
</style>
<link rel="stylesheet" href="/assets/fonts.css?v=1">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalWebPage",
  "name": "Urine colour: meaning and warning signs",
  "description": "What each urine colour means, when it is harmless and which changes should be checked with ISC and a neurogenic bladder.",
  "url": "https://blaseunddarm.de/en/urine-colour.html",
  "lastReviewed": "2026-09-05",
  "author": { "@type": "Person", "name": "André Bajorat", "url": "https://blaseunddarm.de/en/about.html", "description": "Spinal cord injury, ISC user, developer of the Bladder & Bowel Manager app" },
  "publisher": { "@type": "Organization", "name": "blaseunddarm.de", "url": "https://blaseunddarm.de/" },
  "inLanguage": "en"
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "What does cloudy urine mean?", "acceptedAnswer": { "@type": "Answer", "text": "Cloudy urine can indicate a urinary tract infection — especially with ISC and a neurogenic bladder. If cloudiness persists for more than a day or is accompanied by odour, fever or spasticity, the urine should be tested." } },
    { "@type": "Question", "name": "What urine colour is normal?", "acceptedAnswer": { "@type": "Answer", "text": "Light yellow to straw yellow. Very pale urine suggests high fluid intake, dark yellow points to dehydration." } },
    { "@type": "Question", "name": "When is reddish urine an emergency?", "acceptedAnswer": { "@type": "Answer", "text": "A few pink drops after catheterisation may come from minor mucosal irritation. Persistent reddish or brown urine should be checked promptly — especially with pain or fever." } }
  ]
}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

""" + MASTHEAD_EN.format(de_href="/urinfarbe.html") + r"""

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Reference</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">
      What the colour in the bag tells you.
    </h1>
    <p class="lede">
      If you catheterise regularly, you see your urine every time. That is an advantage:
      changes are noticed early. This page explains what the colours mean — and when it is
      worth taking a closer look.
    </p>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Colours at a glance</h2>

      <div class="farbe">
        <div class="farbe__dot" style="background:#f0f0e8"></div>
        <div><h3>Almost colourless</h3><p>Very high fluid intake. Fine with ISC as long as individual volumes stay below 400–500 ml. Discuss with your doctor if you have heart or kidney conditions.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background:#f5e6a0"></div>
        <div><h3>Light yellow / Straw</h3><p>Normal. The pigment urochrome is adequately diluted. Your fluid intake is on track.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background:#e0b830"></div>
        <div><h3>Dark yellow / Amber</h3><p>Not enough fluid. Concentrated urine irritates the bladder lining and encourages UTIs. Drink more — the <a href="/en/fluid-intake.html">fluid intake page</a> explains how much.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background:#c8b898; opacity:.7"></div>
        <div><h3>Cloudy / Milky</h3><p>Often a sign of a <a href="/en/uti-neurogenic-bladder.html">urinary tract infection</a>, especially with odour, fever or increased spasticity. Occasional cloudiness can also come from mucus or sediment — if it lasts longer than a day, have the urine tested.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background:#e8a0a0"></div>
        <div><h3>Pink / Slightly reddish</h3><p>A few pink drops after catheterisation may come from minor mucosal irritation — especially with dry or oversized catheters. If it recurs or increases: have it checked.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background:#b04040"></div>
        <div><h3>Red / Brown</h3><p>Blood in the urine (haematuria). May come from an infection, a stone or an injury. Have it checked promptly — especially with pain, fever or, with SCI at T6 or above, signs of <a href="/en/autonomic-dysreflexia.html">autonomic dysreflexia</a>.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background:#d08020"></div>
        <div><h3>Orange</h3><p>May come from medication (e.g. phenazopyridine), B vitamins or strong concentration. If no medication explains it: have it checked.</p></div>
      </div>
      <div class="farbe">
        <div class="farbe__dot" style="background: linear-gradient(135deg, #80a860 40%, #607840)"></div>
        <div><h3>Greenish</h3><p>Rare. May come from certain bacteria (Pseudomonas), medications or food colourings. Have it checked.</p></div>
      </div>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Why urine colour matters more with ISC</h2>
      <p>With a neurogenic bladder, the usual warning signs are absent: no burning, no conscious urge, often no pain. What remains is what you can see — colour, cloudiness, smell. Noting these briefly at each catheterisation catches an infection or other change earlier than any lab test.</p>
      <p>In the <a href="/en/">Bladder &amp; Bowel Manager</a> app, urine colour can be recorded with a single tap. Persistent cloudiness triggers an alert. Together with the <a href="/en/uti-neurogenic-bladder.html">UTI symptom tracking</a>, it builds a picture that tells more at the next appointment than memory alone.</p>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>When there is no time to wait</h2>
      <div class="hinweis">
        <p><strong>See a doctor promptly:</strong> Persistent reddish or brown urine, fever with flank pain, urine with a strong or unusual smell combined with fatigue or spasticity. With SCI at T6 or above: pounding headache and sweating above the level of injury — <a href="/en/autonomic-dysreflexia.html">signs of autonomic dysreflexia</a>.</p>
      </div>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Why keeping a record helps</h2>
      <p>"How long has the urine been cloudy?" — the question comes up at every appointment. A brief colour note at each catheterisation answers it without guessing. On paper, use the <a href="/en/bladder-diary.html">bladder diary template</a>. The <a href="/en/">Bladder &amp; Bowel Manager</a> app makes it easier: colour and symptoms as one-tap chips, alerts for patterns and a PDF report for the next visit. Everything stays on your device.</p>
    </div>
    <div class="actions" style="margin-top:2.5rem">
      <a class="btn btn--ghost" href="/en/intermittent-catheterisation.html">ISC guide</a>
      <a class="btn btn--ghost" href="/en/uti-neurogenic-bladder.html">Recognise a UTI</a>
      <a class="btn btn--ghost" href="/en/">The app</a>
    </div>
  </section>

  <section class="section wrap" style="margin-top:1rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Sources</h2>
      <ol style="font-size:.85rem;color:var(--ink-soft);padding-left:1.5rem">
        <li>S2k Guideline: Neuro-urological care of patients with spinal cord injury (AWMF 179-001, 2021) <a href="https://register.awmf.org/de/leitlinien/detail/179-001" rel="noopener nofollow" style="color:inherit">↗</a></li>
        <li>Simerville JA et al.: Urinalysis: A Comprehensive Review. <em>Am Fam Physician</em>, 2005 <a href="https://pubmed.ncbi.nlm.nih.gov/15791892/" rel="noopener nofollow" style="color:inherit">↗</a></li>
      </ol>
    </div>
  </section>
""" + AUTHOR_EN + r"""
</main>

""" + FOOTER_EN.format(de_href="/urinfarbe.html")


# ── 3. Wissen Pillar (DE) ────────────────────────────────────

WISSEN_DE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wissen: Ratgeber für neurogene Blase, ISK und Darmmanagement</title>
<meta name="description" content="Ratgeber zu neurogener Blase und Querschnittlähmung: Bristol-Skala, Miktionsprotokoll, ISK, Harnwegsinfekt, autonome Dysreflexie, Trinkmenge und Urinfarbe — verständlich erklärt, von einem Betroffenen.">
<link rel="canonical" href="https://blaseunddarm.de/wissen.html">
<link rel="alternate" hreflang="de" href="https://blaseunddarm.de/wissen.html">
<link rel="alternate" hreflang="en" href="https://blaseunddarm.de/en/knowledge.html">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="Wissen: Ratgeber für neurogene Blase, ISK und Darmmanagement">
<meta property="og:description" content="Alle Ratgeber im Überblick — verständlich erklärt, von einem Betroffenen.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://blaseunddarm.de/wissen.html">
<meta property="og:locale" content="de_DE">
<link rel="stylesheet" href="/assets/style.css">
<style>
  .lede { font-size: clamp(1.05rem, 1rem + 0.4vw, 1.35rem); color: var(--ink-soft); max-width: 48ch; margin: 0 0 2rem; }
  .topic { padding: 1.5rem 0; border-bottom: 1px solid var(--line-soft); }
  .topic:first-of-type { border-top: 1px solid var(--line); }
  .topic h3 { margin: 0 0 .35rem; }
  .topic h3 a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--line-soft); }
  .topic h3 a:hover { border-color: var(--blase); }
  .topic p { margin: 0; font-size: .95rem; color: var(--ink-soft); }
</style>
<link rel="stylesheet" href="/assets/fonts.css?v=1">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Wissen: Ratgeber für neurogene Blase, ISK und Darmmanagement",
  "description": "Übersicht aller Ratgeberseiten auf blaseunddarm.de",
  "url": "https://blaseunddarm.de/wissen.html",
  "publisher": { "@type": "Organization", "name": "blaseunddarm.de", "url": "https://blaseunddarm.de/" },
  "inLanguage": "de"
}
</script>
</head>
<body>
<a class="skip" href="#main">Zum Inhalt springen</a>

""" + MASTHEAD_DE.format(en_href="/en/knowledge.html") + r"""

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Nachschlagen</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">
      Wissen, das im Alltag hilft.
    </h1>
    <p class="lede">
      Sieben Ratgeber zu Blasen- und Darmmanagement bei Querschnittlähmung — geschrieben
      aus eigener Erfahrung, gestützt auf die urologische Fachliteratur.
    </p>
  </section>

  <section class="section wrap">
    <div class="measure">

      <div class="topic">
        <h3><a href="/isk.html">Intermittierender Selbstkatheterismus (ISK)</a></h3>
        <p>Warum katheterisiert wird, wie oft, welche Mengen normal sind, was die Kasse zahlt und welche Warnzeichen keinen Aufschub dulden.</p>
      </div>

      <div class="topic">
        <h3><a href="/miktionsprotokoll.html">Miktionsprotokoll (Blasentagebuch)</a></h3>
        <p>Was eingetragen wird, welche Werte als normal gelten und eine kostenlose PDF-Vorlage zum Ausdrucken.</p>
      </div>

      <div class="topic">
        <h3><a href="/hwi.html">Harnwegsinfekt bei neurogener Blase</a></h3>
        <p>Warum die klassischen Warnzeichen beim ISK oft fehlen, woran man einen Infekt stattdessen erkennt und wann es keinen Aufschub gibt.</p>
      </div>

      <div class="topic">
        <h3><a href="/trinkmenge.html">Trinkmenge bei ISK</a></h3>
        <p>Warum weniger trinken der falsche Weg ist, welche Mengen sinnvoll sind und warum die Bilanz aus Ein- und Ausfuhr zählt.</p>
      </div>

      <div class="topic">
        <h3><a href="/urinfarbe.html">Urinfarbe: Bedeutung und Warnzeichen</a></h3>
        <p>Was jede Farbe bedeutet — von farblos bis rötlich — und welche Veränderungen beim ISK besonders aufmerksam machen sollten.</p>
      </div>

      <div class="topic">
        <h3><a href="/autonome-dysreflexie.html">Autonome Dysreflexie</a></h3>
        <p>Der Notfall, den man kennen muss: welche Zeichen ihn ankündigen, welche Auslöser am häufigsten sind und was sofort zu tun ist.</p>
      </div>

      <div class="topic">
        <h3><a href="/bristol.html">Bristol-Skala</a></h3>
        <p>Die sieben Stuhlformen von Typ 1 bis 7 verständlich erklärt: was sie über die Verdauung verraten und wann ein Arztbesuch ratsam ist.</p>
      </div>

    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <p>
        Alle Seiten sind als allgemeine Information gedacht und ersetzen keine ärztliche
        Beratung. Bei konkreten Beschwerden bitte ärztlichen Rat einholen. Die Daten, die du
        mit diesen Ratgebern sammelst, lassen sich in der
        <a href="/">Blase &amp; Darm Manager App</a> protokollieren — alles bleibt auf deinem Gerät.
      </p>
    </div>
  </section>

</main>

""" + FOOTER_DE.format(en_href="/en/knowledge.html")


# ── 4. Knowledge Pillar (EN) ─────────────────────────────────

WISSEN_EN = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge: guides for neurogenic bladder, ISC and bowel management</title>
<meta name="description" content="Guides on neurogenic bladder and spinal cord injury: Bristol Stool Scale, bladder diary, ISC, urinary tract infection, autonomic dysreflexia, fluid intake and urine colour — explained clearly, by someone who lives it.">
<link rel="canonical" href="https://blaseunddarm.de/en/knowledge.html">
<link rel="alternate" hreflang="en" href="https://blaseunddarm.de/en/knowledge.html">
<link rel="alternate" hreflang="de" href="https://blaseunddarm.de/wissen.html">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="Knowledge: guides for neurogenic bladder, ISC and bowel management">
<meta property="og:description" content="All guides at a glance — explained clearly, by someone who lives it.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://blaseunddarm.de/en/knowledge.html">
<meta property="og:locale" content="en_GB">
<link rel="stylesheet" href="/assets/style.css">
<style>
  .lede { font-size: clamp(1.05rem, 1rem + 0.4vw, 1.35rem); color: var(--ink-soft); max-width: 48ch; margin: 0 0 2rem; }
  .topic { padding: 1.5rem 0; border-bottom: 1px solid var(--line-soft); }
  .topic:first-of-type { border-top: 1px solid var(--line); }
  .topic h3 { margin: 0 0 .35rem; }
  .topic h3 a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--line-soft); }
  .topic h3 a:hover { border-color: var(--blase); }
  .topic p { margin: 0; font-size: .95rem; color: var(--ink-soft); }
</style>
<link rel="stylesheet" href="/assets/fonts.css?v=1">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Knowledge: guides for neurogenic bladder, ISC and bowel management",
  "description": "Overview of all guide pages on blaseunddarm.de",
  "url": "https://blaseunddarm.de/en/knowledge.html",
  "publisher": { "@type": "Organization", "name": "blaseunddarm.de", "url": "https://blaseunddarm.de/" },
  "inLanguage": "en"
}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

""" + MASTHEAD_EN.format(de_href="/wissen.html") + r"""

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Reference</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">
      Knowledge that helps in daily life.
    </h1>
    <p class="lede">
      Seven guides on bladder and bowel management with a spinal cord injury — written
      from personal experience, backed by urological literature.
    </p>
  </section>

  <section class="section wrap">
    <div class="measure">

      <div class="topic">
        <h3><a href="/en/intermittent-catheterisation.html">Intermittent Self-Catheterisation (ISC)</a></h3>
        <p>Why catheterisation is needed, how often, what volumes are normal, insurance coverage and warning signs that need prompt attention.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/bladder-diary.html">Bladder Diary</a></h3>
        <p>What to record, what counts as normal and a free PDF template to print.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/uti-neurogenic-bladder.html">UTI with a Neurogenic Bladder</a></h3>
        <p>Why the usual warning signs are often absent with ISC, what to look for instead and when there is no time to wait.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/fluid-intake.html">Fluid Intake with ISC</a></h3>
        <p>Why drinking less is the wrong approach, what amounts make sense and why the balance of intake and output matters.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/urine-colour.html">Urine Colour: Meaning and Warning Signs</a></h3>
        <p>What each colour means — from colourless to reddish — and which changes should get extra attention with ISC.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/autonomic-dysreflexia.html">Autonomic Dysreflexia</a></h3>
        <p>The emergency you need to know: which signs announce it, the most common triggers and what to do immediately.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/bristol.html">Bristol Stool Scale</a></h3>
        <p>The seven stool types from Type 1 to 7 explained clearly: what they reveal about digestion and when to see a doctor.</p>
      </div>

    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <p>
        All pages are intended as general information and do not replace medical advice.
        If you have specific concerns, please seek medical advice. The data you gather
        with these guides can be recorded in the
        <a href="/en/">Bladder &amp; Bowel Manager app</a> — everything stays on your device.
      </p>
    </div>
  </section>

</main>

""" + FOOTER_EN.format(de_href="/wissen.html")


# ── 5. Sitemap update ────────────────────────────────────────

NEW_SITEMAP_ENTRIES = """  <url><loc>https://blaseunddarm.de/wissen.html</loc><priority>1.0</priority></url>
  <url><loc>https://blaseunddarm.de/en/knowledge.html</loc><priority>0.8</priority></url>
  <url><loc>https://blaseunddarm.de/urinfarbe.html</loc><priority>0.9</priority></url>
  <url><loc>https://blaseunddarm.de/en/urine-colour.html</loc><priority>0.7</priority></url>"""


# ── Main ──────────────────────────────────────────────────────

def run():
    os.chdir(ROOT)

    # 1. Create new pages
    print("═══ Neue Seiten ═══")

    p = ROOT / "urinfarbe.html"
    if not p.exists():
        safe_write(p, URINFARBE_DE)
    else:
        print(f"  ⏭  urinfarbe.html existiert bereits")

    p = ROOT / "en" / "urine-colour.html"
    if not p.exists():
        safe_write(p, URINFARBE_EN)
    else:
        print(f"  ⏭  en/urine-colour.html existiert bereits")

    p = ROOT / "wissen.html"
    if not p.exists():
        safe_write(p, WISSEN_DE)
    else:
        print(f"  ⏭  wissen.html existiert bereits")

    p = ROOT / "en" / "knowledge.html"
    if not p.exists():
        safe_write(p, WISSEN_EN)
    else:
        print(f"  ⏭  en/knowledge.html existiert bereits")

    # 2. Sitemap
    print("\n═══ Sitemap ═══")
    sm = ROOT / "sitemap.xml"
    text = sm.read_text("utf-8")
    if "urinfarbe.html" not in text:
        text = text.replace("</urlset>", NEW_SITEMAP_ENTRIES + "\n</urlset>")
        sm.write_text(text, "utf-8")
        print("  ✅ sitemap.xml: 4 neue URLs ergänzt")
    else:
        print("  ⏭  sitemap.xml: URLs bereits vorhanden")

    # 3. Add Urinfarbe to footer of existing knowledge pages
    print("\n═══ Footer-Links: Urinfarbe ═══")
    de_pages = ["isk.html", "hwi.html", "autonome-dysreflexie.html",
                "trinkmenge.html", "miktionsprotokoll.html", "bristol.html"]
    for fn in de_pages:
        p = ROOT / fn
        if not p.exists():
            continue
        text = p.read_text("utf-8")
        if "/urinfarbe.html" not in text and '<a href="/trinkmenge.html">Trinkmenge</a>' in text:
            text = text.replace(
                '<a href="/trinkmenge.html">Trinkmenge</a>',
                '<a href="/trinkmenge.html">Trinkmenge</a>\n        <a href="/urinfarbe.html">Urinfarbe</a>'
            )
            p.write_text(text, "utf-8")
            print(f"  ✅ {fn}: Urinfarbe-Link im Footer ergänzt")

    en_pages = ["en/intermittent-catheterisation.html", "en/uti-neurogenic-bladder.html",
                "en/autonomic-dysreflexia.html", "en/fluid-intake.html",
                "en/bladder-diary.html", "en/bristol.html"]
    for fn in en_pages:
        p = ROOT / fn
        if not p.exists():
            continue
        text = p.read_text("utf-8")
        if "/en/urine-colour.html" not in text and '<a href="/en/fluid-intake.html">' in text:
            text = text.replace(
                '<a href="/en/fluid-intake.html">Fluid Intake</a>',
                '<a href="/en/fluid-intake.html">Fluid Intake</a>\n        <a href="/en/urine-colour.html">Urine Colour</a>'
            )
            p.write_text(text, "utf-8")
            print(f"  ✅ {fn}: Urine Colour link added to footer")

    # Summary
    print(f"\n{'='*50}")
    if ERRORS:
        print(f"⚠️  {len(ERRORS)} Probleme:")
        for e in ERRORS:
            print(f"   • {e}")
    else:
        print("✅ Alle Änderungen fehlerfrei.")

    print(f"\nDeploy:")
    print(f"  cd /var/www/blaseunddarm")
    print(f"  python3 seo-seiten.py")
    print(f'  git add -A && git commit -m "SEO: Urinfarbe + Wissen-Pillar + Sitemap" && git push')

if __name__ == "__main__":
    run()
