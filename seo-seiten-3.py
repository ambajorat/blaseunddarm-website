#!/usr/bin/env python3
"""
SEO Runde 3: Darmmanagement + Katheter & Rezept
=================================================
1. darmmanagement.html (DE) + en/bowel-management.html (EN)
2. katheter-rezept.html (DE) + en/catheter-prescription.html (EN)
3. sitemap.xml ergänzen
4. Footer + Wissen-Pillar aktualisieren
5. Internal Links auf bestehenden Seiten

Lauf: cd /var/www/blaseunddarm && python3 seo-seiten-3.py
Danach: git add -A && git commit -m "SEO: Darmmanagement + Katheter-Rezept" && git push
"""
import os, json, re
from pathlib import Path

ROOT = Path(__file__).parent
ERRORS = []

def safe_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, "utf-8")
    print(f"  ✅ {path.relative_to(ROOT)} geschrieben")

def patch_replace(path, old, new, label=""):
    text = path.read_text("utf-8")
    if new.strip()[:50] in text:
        print(f"  ⏭  {path.name}: {label} bereits vorhanden")
        return True
    if old not in text:
        ERRORS.append(f"Anker nicht gefunden in {path.name}: {label or old[:50]}")
        return False
    path.write_text(text.replace(old, new, 1), "utf-8")
    print(f"  ✅ {path.name}: {label}")
    return True

# ── Shared building blocks ─────────────────────────────────────

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="de" href="{href_de}">
<link rel="alternate" hreflang="en" href="{href_en}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="{og_locale}">
<link rel="stylesheet" href="/assets/style.css">
<style>
  .lede {{ font-size: clamp(1.05rem, 1rem + 0.4vw, 1.35rem); color: var(--ink-soft); max-width: 48ch; margin: 0 0 2rem; }}
  .hinweis {{ border-left: 3px solid var(--blase); background: var(--surface); padding: 1.25rem 1.5rem; margin: 2rem 0; font-size: 0.95rem; }}
  .hinweis p {{ margin: 0; color: var(--ink-soft); }}
  .hinweis strong {{ color: var(--ink); }}
</style>
<link rel="stylesheet" href="/assets/fonts.css?v=1">
{jsonld}
</head>"""

def masthead_de(en_href):
    return f"""<body>
<a class="skip" href="#main">Zum Inhalt springen</a>
<header class="masthead">
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

def masthead_en(de_href):
    return f"""<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
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

AUTHOR_DE = """
  <section class="section wrap" style="margin-top:3rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Über den Autor</h2>
      <p style="font-size:.95rem">
        André Bajorat ist querschnittgelähmt und katheterisiert sich seit 2025 selbst.
        Er hat die App <a href="/">Blase &amp; Darm Manager</a> entwickelt und schreibt auf
        <a href="https://ploetzlich-querschnitt.de" rel="noopener">plötzlich querschnitt</a>
        über das Leben mit Querschnittlähmung.
      </p>
    </div>
  </section>"""

AUTHOR_EN = """
  <section class="section wrap" style="margin-top:3rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">About the author</h2>
      <p style="font-size:.95rem">
        André Bajorat has a spinal cord injury and has been self-catheterising since 2025.
        He built the <a href="/en/">Bladder &amp; Bowel Manager</a> app and writes about
        life with SCI at <a href="https://ploetzlich-querschnitt.de" rel="noopener">plötzlich querschnitt</a>.
      </p>
    </div>
  </section>"""

def footer_de(en_href):
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot__inner">
      <span>© <span id="jahr">2026</span> Blase &amp; Darm Manager</span>
      <nav aria-label="Rechtliches">
        <a href="https://ploetzlich-querschnitt.de">plötzlich querschnitt</a>
        <a href="/">Start</a>
        <a href="/wissen.html">Wissen</a>
        <a href="/support.html">Support</a>
        <a href="/datenschutz.html">Datenschutz</a>
        <a href="/impressum.html">Impressum</a>
        <a href="{en_href}" hreflang="en" lang="en">English</a>
      </nav>
    </div>
    <p class="disclaimer">Diese Seite dient der allgemeinen Information und ersetzt keine ärztliche Beratung, Diagnose oder Behandlung.</p>
    <p class="marken">Apple, das Apple-Logo, iPhone, iPad, Apple Watch, Siri und CarPlay sind Marken von Apple Inc., eingetragen in den USA und anderen Ländern. App Store ist eine Dienstleistungsmarke von Apple Inc. Diese Website steht in keiner Verbindung zu Apple Inc.</p>
    <p><a class="nach-oben" href="#main">↑ Nach oben</a></p>
  </div>
</footer>
<script>document.getElementById('jahr').textContent=new Date().getFullYear();</script>
</body></html>"""

def footer_en(de_href):
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot__inner">
      <span>© <span id="jahr">2026</span> Bladder &amp; Bowel Manager</span>
      <nav aria-label="Legal">
        <a href="https://ploetzlich-querschnitt.de">plötzlich querschnitt</a>
        <a href="/en/">Home</a>
        <a href="/en/knowledge.html">Knowledge</a>
        <a href="/en/support.html">Support</a>
        <a href="/en/privacy.html">Privacy</a>
        <a href="/en/imprint.html">Imprint</a>
        <a href="{de_href}" hreflang="de" lang="de">Deutsch</a>
      </nav>
    </div>
    <p class="disclaimer">This page is for general information only and does not replace medical advice, diagnosis or treatment.</p>
    <p class="marken">Apple, the Apple logo, iPhone, iPad, Apple Watch, Siri and CarPlay are trademarks of Apple Inc. App Store is a service mark of Apple Inc. This website is not affiliated with Apple Inc.</p>
    <p><a class="nach-oben" href="#main">↑ To the top</a></p>
  </div>
</footer>
<script>document.getElementById('jahr').textContent=new Date().getFullYear();</script>
</body></html>"""

def sources_de(items):
    li = "\n".join(f'        <li>{t}' + (f' <a href="{u}" rel="noopener nofollow" style="color:inherit">↗</a>' if u else '') + '</li>' for t,u in items)
    return f"""
  <section class="section wrap" style="margin-top:1rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Quellen</h2>
      <ol style="font-size:.85rem;color:var(--ink-soft);padding-left:1.5rem">
{li}
      </ol>
    </div>
  </section>"""

def sources_en(items):
    li = "\n".join(f'        <li>{t}' + (f' <a href="{u}" rel="noopener nofollow" style="color:inherit">↗</a>' if u else '') + '</li>' for t,u in items)
    return f"""
  <section class="section wrap" style="margin-top:1rem">
    <div class="measure">
      <h2 style="font-size:1.1rem;margin-bottom:.75rem">Sources</h2>
      <ol style="font-size:.85rem;color:var(--ink-soft);padding-left:1.5rem">
{li}
      </ol>
    </div>
  </section>"""

# ═══════════════════════════════════════════════════════════════
# DARMMANAGEMENT
# ═══════════════════════════════════════════════════════════════

DARM_JSONLD_DE = json.dumps({"@context":"https://schema.org","@type":"MedicalWebPage","name":"Darmmanagement bei Querschnittlähmung","description":"Neurogene Darmfunktionsstörung verstehen: reflexiver und schlaffer Darm, Abführrhythmus, Ernährung und Dokumentation.","url":"https://blaseunddarm.de/darmmanagement.html","lastReviewed":"2026-09-05","author":{"@type":"Person","name":"André Bajorat","url":"https://blaseunddarm.de/ueber-mich.html","description":"Querschnittgelähmt, App-Entwickler"},"publisher":{"@type":"Organization","name":"blaseunddarm.de","url":"https://blaseunddarm.de/"},"inLanguage":"de"}, ensure_ascii=False, indent=2)

DARM_FAQ_DE = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
    {"@type":"Question","name":"Was ist ein neurogener Darm?","acceptedAnswer":{"@type":"Answer","text":"Bei einer Querschnittlähmung ist die Steuerung der Darmentleerung gestört. Je nach Lähmungshöhe entsteht ein reflexiver Darm (Läsion oberhalb Conus medullaris, erhöhter Tonus) oder ein schlaffer Darm (Läsion im Bereich Conus/Cauda, verminderter Tonus). Beide Formen erfordern ein individuelles Darmmanagement."}},
    {"@type":"Question","name":"Wie oft sollte der Darm entleert werden?","acceptedAnswer":{"@type":"Answer","text":"Die meisten Betroffenen finden einen Rhythmus von einem Tag bis maximal drei Tagen. Wichtig ist die Regelmäßigkeit: feste Zeiten, feste Abfolge, Geduld — und ein Abführplan, der mit dem Querschnittzentrum abgestimmt ist."}},
    {"@type":"Question","name":"Welche Rolle spielt die Ernährung beim Darmmanagement?","acceptedAnswer":{"@type":"Answer","text":"Eine ballaststoffreiche Ernährung (Ziel: 25–30 g pro Tag), ausreichend Flüssigkeit (1,5–2 Liter) und regelmäßige Essenszeiten unterstützen die Darmmotilität. Der gastrokolische Reflex — Essen oder Trinken regt die Darmbewegung an — lässt sich gezielt nutzen."}}
]}, ensure_ascii=False, indent=2)

DARM_DE = (
    HEAD_TEMPLATE.format(
        lang="de",
        title="Darmmanagement bei Querschnittlähmung — Rhythmus statt Zufall",
        desc="Neurogene Darmfunktionsstörung bei Querschnittlähmung: reflexiver und schlaffer Darm, Abführrhythmus, Ernährung, Hilfsmittel und warum Dokumentation hilft.",
        canonical="https://blaseunddarm.de/darmmanagement.html",
        href_de="https://blaseunddarm.de/darmmanagement.html",
        href_en="https://blaseunddarm.de/en/bowel-management.html",
        og_title="Darmmanagement bei Querschnittlähmung",
        og_desc="Reflexiver und schlaffer Darm, Abführrhythmus, Ernährung — verständlich erklärt.",
        og_locale="de_DE",
        jsonld=f'<script type="application/ld+json">\n{DARM_JSONLD_DE}\n</script>\n<script type="application/ld+json">\n{DARM_FAQ_DE}\n</script>',
    )
    + "\n" + masthead_de("/en/bowel-management.html") + """

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Nachschlagen</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">
      Darm: Rhythmus statt Zufall.
    </h1>
    <p class="lede">
      Über das Blasenmanagement wird viel geschrieben. Über den Darm weniger — obwohl er
      den Alltag mindestens genauso stark beeinflusst. Diese Seite erklärt die Grundlagen
      der neurogenen Darmfunktionsstörung und was im Alltag hilft.
    </p>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Was ist ein neurogener Darm?</h2>
      <p>
        Bei einer Querschnittlähmung ist die willkürliche Steuerung der Darmentleerung
        gestört. Der Darm selbst funktioniert weiter — aber die Kommunikation zwischen Darm
        und Gehirn ist unterbrochen. Das betrifft sowohl das Empfinden von Stuhldrang als
        auch die Kontrolle über den Schließmuskel.
      </p>
      <p>
        Je nach Höhe und Art der Lähmung unterscheidet man zwei Formen:
      </p>

      <h3 style="margin-top:1.5rem">Reflexiver Darm (oberes motorisches Neuron)</h3>
      <p>
        Bei einer Läsion oberhalb des Conus medullaris bleibt der Tonus des Schließmuskels
        erhalten oder ist erhöht. Der Darm reagiert auf Dehnungsreize mit Reflexaktivität —
        das lässt sich für ein geplantes Abführen nutzen (digitale Stimulation,
        Zäpfchen, Klysmen). Die meisten Menschen mit thorakaler oder zervikaler
        Querschnittlähmung haben einen reflexiven Darm.
      </p>

      <h3 style="margin-top:1.5rem">Schlaffer Darm (unteres motorisches Neuron)</h3>
      <p>
        Bei einer Läsion im Bereich Conus medullaris oder Cauda equina ist der Tonus
        des Schließmuskels vermindert. Es fehlt die Reflexaktivität — das Abführen
        stützt sich stärker auf Bauchpresse, manuelle Ausräumung und stuhlregulierende
        Maßnahmen. Das Inkontinenzrisiko ist hier oft höher.
      </p>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Wie oft sollte der Darm entleert werden?</h2>
      <p>
        Die meisten Betroffenen finden einen Rhythmus von einem Tag bis maximal drei Tagen.
        Entscheidend ist weniger die Frequenz als die Regelmäßigkeit: feste Zeiten, feste
        Abfolge, keine Hektik. Ein Abführplan wird in der Reha mit dem Querschnittzentrum
        erarbeitet und danach im Alltag angepasst.
      </p>

      <div class="hinweis">
        <p>
          <strong>Faustregel:</strong> Eine Änderung am Darmmanagement erst nach 3–5
          Stuhlentleerungen bzw. einer Woche beurteilen. Der Darm reagiert langsam —
          vorschnelle Wechsel machen die Sache schlechter, nicht besser.
        </p>
      </div>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Was im Alltag hilft</h2>

      <h3 style="margin-top:1.5rem">Ernährung</h3>
      <p>
        Ballaststoffe (Ziel: 25–30 g am Tag, langsam steigern ab 15 g), ausreichend
        Flüssigkeit (1,5–2 Liter, siehe <a href="/trinkmenge.html">Trinkmenge</a>) und
        regelmäßige Essenszeiten. Der gastrokolische Reflex — Essen oder Trinken regt die
        Darmbewegung an — lässt sich gezielt nutzen, indem man das Abführen kurz nach einer
        Mahlzeit plant.
      </p>

      <h3 style="margin-top:1.5rem">Bewegung</h3>
      <p>
        Jede Form von Bewegung unterstützt die Darmmotilität. Rollstuhlsport, Transfers,
        Physiotherapie — alles besser als Stillsitzen.
      </p>

      <h3 style="margin-top:1.5rem">Dokumentation</h3>
      <p>
        Stuhlfrequenz, Konsistenz (die <a href="/bristol.html">Bristol-Skala</a> hilft),
        Dauer und besondere Vorkommnisse notieren. Zwei Wochen Dokumentation zeigen, ob der
        Rhythmus stimmt — und geben dem Arzt eine Grundlage, die besser ist als
        „eigentlich ganz okay".
      </p>
      <p>
        Der <a href="/">Blase &amp; Darm Manager</a> protokolliert Stuhlgang mit
        Bristol-Typ, Menge (von 🐜 bis 🐘) und Uhrzeit. Die Statistik zeigt den
        durchschnittlichen Abstand und die Konsistenzverteilung. Ein PDF-Bericht fasst
        alles für den nächsten Termin zusammen.
      </p>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Wann es keinen Aufschub gibt</h2>
      <div class="hinweis">
        <p>
          <strong>Sofort ärztlich abklären:</strong> Stuhlinkontinenz, die sich plötzlich
          verschlechtert. Keine Stuhlentleerung seit mehr als drei Tagen trotz aller
          Maßnahmen. Bauchschmerzen oder Blähbauch mit Übelkeit. Blut im Stuhl.
          Bei Querschnittlähmung ab Th6: pochender Kopfschmerz und Schwitzen —
          <a href="/autonome-dysreflexie.html">Zeichen einer autonomen Dysreflexie</a>,
          deren Auslöser auch ein voller Darm sein kann.
        </p>
      </div>
    </div>
  </section>

  <section class="section wrap">
    <div class="measure">
      <h2>Weiterführende Seiten</h2>
      <p>
        <a href="/bristol.html">Bristol-Skala</a> · <a href="/trinkmenge.html">Trinkmenge</a> ·
        <a href="/isk.html">ISK</a> · <a href="/autonome-dysreflexie.html">Autonome Dysreflexie</a> ·
        <a href="/">Zur App</a>
      </p>
    </div>
  </section>
"""
    + sources_de([
        ("Leitlinie Neurogene Darmfunktionsstörung bei Querschnittlähmung (DMGP/AWMF, 2020)", "https://link.springer.com/article/10.1007/s00053-020-00482-5"),
        ("Darmmanagement: Sechs Punkte für eine geplante Entleerung (der-querschnitt.de)", "https://www.der-querschnitt.de/darmfunktionsstoerung-querschnittlaehmung-66175"),
        ("Kompendium Neurogene Darmfunktionsstörung (Manfred-Sauer-Stiftung, 2011)", "https://www.manfred-sauer.com/wp-content/uploads/2023/02/AK-Darmmanagement-Querschnittgelaehmter_Kompendium_Neurogene-Darmfunktionsstoerung-bei-QSL.pdf"),
    ])
    + AUTHOR_DE
    + "\n</main>\n\n"
    + footer_de("/en/bowel-management.html")
)

# ── Bowel Management EN ───────────────────────────────────────

DARM_JSONLD_EN = json.dumps({"@context":"https://schema.org","@type":"MedicalWebPage","name":"Bowel management with a spinal cord injury","description":"Neurogenic bowel dysfunction explained: reflex and flaccid bowel, bowel routine, diet and documentation.","url":"https://blaseunddarm.de/en/bowel-management.html","lastReviewed":"2026-09-05","author":{"@type":"Person","name":"André Bajorat","url":"https://blaseunddarm.de/en/about.html","description":"Spinal cord injury, ISC user, app developer"},"publisher":{"@type":"Organization","name":"blaseunddarm.de","url":"https://blaseunddarm.de/"},"inLanguage":"en"}, ensure_ascii=False, indent=2)
DARM_FAQ_EN = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
    {"@type":"Question","name":"What is a neurogenic bowel?","acceptedAnswer":{"@type":"Answer","text":"With a spinal cord injury, voluntary control of bowel emptying is impaired. Depending on injury level, this results in a reflex bowel (lesion above the conus medullaris, increased tone) or a flaccid bowel (lesion at conus/cauda level, reduced tone). Both require an individualised bowel management programme."}},
    {"@type":"Question","name":"How often should the bowel be emptied?","acceptedAnswer":{"@type":"Answer","text":"Most people find a rhythm of one to three days. Regularity matters more than frequency: fixed times, a consistent routine and patience — developed with the spinal cord centre."}},
    {"@type":"Question","name":"What role does diet play in bowel management?","acceptedAnswer":{"@type":"Answer","text":"A high-fibre diet (target: 25–30 g per day), adequate fluids (1.5–2 litres) and regular meal times support gut motility. The gastrocolic reflex — eating or drinking stimulates bowel movement — can be used deliberately by scheduling bowel care shortly after a meal."}}
]}, ensure_ascii=False, indent=2)

DARM_EN = (
    HEAD_TEMPLATE.format(
        lang="en",
        title="Bowel management with a spinal cord injury — routine over chance",
        desc="Neurogenic bowel dysfunction with SCI explained: reflex and flaccid bowel, bowel routine, diet, aids and why documentation helps.",
        canonical="https://blaseunddarm.de/en/bowel-management.html",
        href_de="https://blaseunddarm.de/darmmanagement.html",
        href_en="https://blaseunddarm.de/en/bowel-management.html",
        og_title="Bowel management with a spinal cord injury",
        og_desc="Reflex and flaccid bowel, routine, diet — explained clearly.",
        og_locale="en_GB",
        jsonld=f'<script type="application/ld+json">\n{DARM_JSONLD_EN}\n</script>\n<script type="application/ld+json">\n{DARM_FAQ_EN}\n</script>',
    )
    + "\n" + masthead_en("/darmmanagement.html") + """

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Reference</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">Bowel: routine over chance.</h1>
    <p class="lede">Much is written about bladder management. Less about the bowel — even though it affects daily life just as much. This page covers the basics of neurogenic bowel dysfunction and what helps in practice.</p>
  </section>

  <section class="section wrap"><div class="measure">
    <h2>What is a neurogenic bowel?</h2>
    <p>With a spinal cord injury, voluntary bowel control is impaired. The bowel itself still works — but communication between bowel and brain is disrupted. This affects both the sensation of needing to go and control of the sphincter.</p>
    <p>Depending on injury level, there are two types:</p>
    <h3 style="margin-top:1.5rem">Reflex bowel (upper motor neuron)</h3>
    <p>With a lesion above the conus medullaris, sphincter tone is preserved or increased. The bowel responds to stretch with reflex activity — useful for planned emptying (digital stimulation, suppositories, mini enemas). Most people with thoracic or cervical SCI have a reflex bowel.</p>
    <h3 style="margin-top:1.5rem">Flaccid bowel (lower motor neuron)</h3>
    <p>With a lesion at conus medullaris or cauda equina level, sphincter tone is reduced. Reflex activity is absent — emptying relies more on abdominal pressure, manual evacuation and stool regulation. The risk of incontinence is often higher.</p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>How often should the bowel be emptied?</h2>
    <p>Most people find a rhythm of one to three days. What matters is regularity: fixed times, a consistent sequence, no rush. A bowel plan is developed in rehab with the spinal cord centre and then adapted in daily life.</p>
    <div class="hinweis"><p><strong>Rule of thumb:</strong> Judge a change in bowel management only after 3–5 bowel movements or one week. The gut responds slowly — hasty changes make things worse, not better.</p></div>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>What helps in daily life</h2>
    <h3 style="margin-top:1.5rem">Diet</h3>
    <p>Fibre (target: 25–30 g per day, increase gradually from 15 g), adequate fluids (1.5–2 litres, see <a href="/en/fluid-intake.html">fluid intake</a>) and regular meal times. The gastrocolic reflex — eating or drinking stimulates bowel activity — can be used deliberately by planning bowel care shortly after a meal.</p>
    <h3 style="margin-top:1.5rem">Movement</h3>
    <p>Any form of movement supports gut motility. Wheelchair sports, transfers, physiotherapy — anything beats sitting still.</p>
    <h3 style="margin-top:1.5rem">Documentation</h3>
    <p>Record stool frequency, consistency (the <a href="/en/bristol.html">Bristol Stool Scale</a> helps), duration and anything unusual. Two weeks of documentation shows whether the routine is working — and gives the doctor a basis far better than "it's been more or less okay".</p>
    <p>The <a href="/en/">Bladder &amp; Bowel Manager</a> app logs bowel movements with Bristol type, amount (from 🐜 to 🐘) and time. Statistics show average intervals and consistency distribution. A PDF report summarises everything for the next appointment.</p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>When there is no time to wait</h2>
    <div class="hinweis"><p><strong>See a doctor promptly:</strong> Faecal incontinence that suddenly worsens. No bowel movement for more than three days despite all measures. Abdominal pain or bloating with nausea. Blood in stool. With SCI at T6 or above: pounding headache and sweating — <a href="/en/autonomic-dysreflexia.html">signs of autonomic dysreflexia</a>, which can also be triggered by a full bowel.</p></div>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Related pages</h2>
    <p><a href="/en/bristol.html">Bristol Stool Scale</a> · <a href="/en/fluid-intake.html">Fluid Intake</a> · <a href="/en/intermittent-catheterisation.html">ISC</a> · <a href="/en/autonomic-dysreflexia.html">Autonomic Dysreflexia</a> · <a href="/en/">The app</a></p>
  </div></section>
"""
    + sources_en([
        ("Guideline: Neurogenic bowel dysfunction in SCI (DMGP/AWMF, 2020)", "https://link.springer.com/article/10.1007/s00053-020-00482-5"),
        ("Bowel management: six points for planned emptying (der-querschnitt.de)", "https://www.der-querschnitt.de/darmfunktionsstoerung-querschnittlaehmung-66175"),
    ])
    + AUTHOR_EN + "\n</main>\n\n" + footer_en("/darmmanagement.html")
)

# ═══════════════════════════════════════════════════════════════
# KATHETER & REZEPT
# ═══════════════════════════════════════════════════════════════

KR_JSONLD_DE = json.dumps({"@context":"https://schema.org","@type":"MedicalWebPage","name":"ISK-Katheter auf Rezept: Verordnung, Kostenübernahme, Bestand","description":"Wie ISK-Katheter verordnet werden, was die Kasse zahlt, worauf beim Rezept zu achten ist und wie man den Bestand im Griff behält.","url":"https://blaseunddarm.de/katheter-rezept.html","lastReviewed":"2026-09-05","author":{"@type":"Person","name":"André Bajorat","url":"https://blaseunddarm.de/ueber-mich.html"},"publisher":{"@type":"Organization","name":"blaseunddarm.de","url":"https://blaseunddarm.de/"},"inLanguage":"de"}, ensure_ascii=False, indent=2)
KR_FAQ_DE = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
    {"@type":"Question","name":"Wer zahlt meine ISK-Katheter?","acceptedAnswer":{"@type":"Answer","text":"Bei ärztlicher Verordnung übernimmt die gesetzliche Krankenkasse die Kosten. Die Versorgung läuft über zugelassene Hilfsmittelversorger (z. B. PubliCare, GHD, Manfred Sauer). Eine Zuzahlung von maximal 10 Euro pro Monat kann anfallen, sofern keine Befreiung vorliegt."}},
    {"@type":"Question","name":"Was muss auf dem Katheter-Rezept stehen?","acceptedAnswer":{"@type":"Answer","text":"Diagnose (z. B. neurogene Blasenentleerungsstörung), Produktname und Hersteller, Charrière-Größe, Stückzahl pro Tag, Verordnungszeitraum. Ist das Feld 'aut idem' angekreuzt, darf der Versorger kein anderes Produkt liefern."}},
    {"@type":"Question","name":"Wie behalte ich den Überblick über meinen Katheterbestand?","acceptedAnswer":{"@type":"Answer","text":"Die App Blase & Darm Manager zählt den Bestand bei jedem Katheterisieren automatisch herunter, warnt rechtzeitig vor dem Ende und zeigt, wann das Rezept erneuert werden muss."}}
]}, ensure_ascii=False, indent=2)

KATHETER_DE = (
    HEAD_TEMPLATE.format(
        lang="de",
        title="ISK-Katheter auf Rezept: Verordnung, Kosten und Bestandsplanung",
        desc="ISK-Katheter auf Rezept: wie die Verordnung funktioniert, was die Krankenkasse zahlt, worauf beim Hilfsmittelrezept zu achten ist und wie man den Bestand im Griff behält.",
        canonical="https://blaseunddarm.de/katheter-rezept.html",
        href_de="https://blaseunddarm.de/katheter-rezept.html",
        href_en="https://blaseunddarm.de/en/catheter-prescription.html",
        og_title="ISK-Katheter auf Rezept",
        og_desc="Verordnung, Kostenübernahme und Bestandsplanung — verständlich erklärt.",
        og_locale="de_DE",
        jsonld=f'<script type="application/ld+json">\n{KR_JSONLD_DE}\n</script>\n<script type="application/ld+json">\n{KR_FAQ_DE}\n</script>',
    )
    + "\n" + masthead_de("/en/catheter-prescription.html") + """

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Nachschlagen</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">
      Katheter auf Rezept — und immer genug da.
    </h1>
    <p class="lede">
      Wer sich selbst katheterisiert, braucht jeden Tag Material. Die Kosten trägt die
      Krankenkasse — aber das Rezept muss stimmen, und der Bestand muss reichen. Diese
      Seite erklärt den Weg vom Arzt bis zur Lieferung.
    </p>
  </section>

  <section class="section wrap"><div class="measure">
    <h2>Wer zahlt meine ISK-Katheter?</h2>
    <p>
      ISK-Katheter sind Hilfsmittel. Bei ärztlicher Verordnung übernimmt die gesetzliche
      Krankenkasse die Kosten vollständig — abzüglich der gesetzlichen Zuzahlung (maximal
      10 Euro pro Monat, sofern keine Befreiung vorliegt). Privat Versicherte klären den
      Umfang mit ihrer Versicherung.
    </p>
    <p>
      Die Versorgung läuft nicht über die Apotheke, sondern über zugelassene
      Hilfsmittelversorger — zum Beispiel PubliCare, GHD GesundHeits GmbH oder
      Manfred Sauer. Diese übernehmen auch die Anleitung und Beratung.
    </p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Was muss auf dem Rezept stehen?</h2>
    <p>Ein Hilfsmittelrezept für ISK-Katheter braucht:</p>
    <ul>
      <li><strong>Feld 7</strong> (Hilfsmittel) angekreuzt</li>
      <li><strong>Diagnose</strong> — z. B. „neurogene Blasenentleerungsstörung bei Querschnittlähmung"</li>
      <li><strong>Produktname und Hersteller</strong> — z. B. „Coloplast SpeediCath Compact Set"</li>
      <li><strong>Charrière-Größe</strong> und ggf. Spitzenform (Nelaton, Tiemann)</li>
      <li><strong>Stückzahl pro Tag</strong> und <strong>Verordnungszeitraum</strong> — z. B. „6×/Tag, 3 Monate"</li>
    </ul>

    <div class="hinweis">
      <p>
        <strong>Tipp: aut idem ankreuzen.</strong> Ist dieses Feld markiert, darf der
        Hilfsmittelversorger kein anderes Produkt liefern. Ohne das Kreuz kann er ein
        „vergleichbares" Produkt wählen — das nicht immer passt. Falls der Arzt zögert:
        die medizinische Begründung ist, dass beim ISK Katheterbeschichtung und Handling
        individuell angepasst werden und ein Produktwechsel Komplikationen riskiert.
      </p>
    </div>

    <p>
      Zusätzlich zu den Kathetern können auf demselben oder einem separaten Rezept
      Zubehör verordnet werden: Urinbeutel, Handschuhe, und — seit der
      OTC-Ausnahmeregelung — auch Antiseptika (z. B. Octenisept) und Gleitmittel
      zur Katheterisierung.
    </p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Dauerverordnung: nicht jedes Quartal zum Arzt</h2>
    <p>
      Bei stabilem Bedarf kann der Arzt eine Dauerverordnung ausstellen. Der
      Hilfsmittelversorger reicht sie bei der Kasse ein; bei Genehmigung gilt sie bis auf
      Widerruf. Das spart Arztbesuche — aber: Wenn sich der Bedarf ändert (andere Größe,
      andere Frequenz), muss ein neues Rezept her.
    </p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Bestand im Griff behalten</h2>
    <p>
      Sechs Katheter am Tag, drei Monate Rezept — das sind 540 Stück. Klingt viel, ist
      schneller aufgebraucht als gedacht. Wer den Bestand nicht zählt, steht irgendwann
      am Wochenende ohne Katheter da.
    </p>
    <p>
      Der <a href="/">Blase &amp; Darm Manager</a> löst das: bei jedem Katheterisieren wird
      ein Stück abgezogen, die Reichweite in Tagen angezeigt und rechtzeitig gewarnt. Wer
      mehrere Kathetersorten nutzt, behält beide Bestände im Blick. Seit Version 4.13
      erkennt der Packungsscanner Barcode und Aufdruck — Name, Charrière und Material
      werden automatisch übernommen.
    </p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Weiterführende Seiten</h2>
    <p>
      <a href="/isk.html">ISK-Ratgeber</a> ·
      <a href="/hwi.html">Harnwegsinfekt erkennen</a> ·
      <a href="/trinkmenge.html">Trinkmenge</a> ·
      <a href="/">Zur App</a>
    </p>
  </div></section>
"""
    + sources_de([
        ("Hilfsmittel-Richtlinie des G-BA (§ 92 SGB V)", ""),
        ("Hilfsmittelverzeichnis des GKV-Spitzenverbandes, Produktgruppe 15 (Inkontinenzhilfen)", ""),
        ("Selbsthilfeverband Inkontinenz: Katheter-Rezept richtig ausstellen", "https://www.selbsthilfeverband-inkontinenz.org/svi_suite/svisuite/tipps_katheter_rezept.php"),
    ])
    + AUTHOR_DE + "\n</main>\n\n" + footer_de("/en/catheter-prescription.html")
)

# ── Catheter Prescription EN ─────────────────────────────────

KR_JSONLD_EN = json.dumps({"@context":"https://schema.org","@type":"MedicalWebPage","name":"ISC catheters on prescription: coverage, ordering and stock tracking","description":"How ISC catheters are prescribed in Germany, what insurance covers and how to keep track of stock.","url":"https://blaseunddarm.de/en/catheter-prescription.html","lastReviewed":"2026-09-05","author":{"@type":"Person","name":"André Bajorat","url":"https://blaseunddarm.de/en/about.html"},"publisher":{"@type":"Organization","name":"blaseunddarm.de","url":"https://blaseunddarm.de/"},"inLanguage":"en"}, ensure_ascii=False, indent=2)
KR_FAQ_EN = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
    {"@type":"Question","name":"Who pays for ISC catheters in Germany?","acceptedAnswer":{"@type":"Answer","text":"With a doctor's prescription, statutory health insurance covers the cost. Supply runs through licensed medical suppliers (e.g. PubliCare, GHD). A co-payment of up to 10 euros per month may apply unless the patient is exempt."}},
    {"@type":"Question","name":"What must a catheter prescription include?","acceptedAnswer":{"@type":"Answer","text":"Diagnosis, product name and manufacturer, Charrière size, quantity per day and prescription period. If the 'aut idem' field is ticked, the supplier may not substitute a different product."}},
    {"@type":"Question","name":"How do I keep track of my catheter stock?","acceptedAnswer":{"@type":"Answer","text":"The Bladder & Bowel Manager app counts down the stock with each catheterisation, warns before it runs out and shows when the prescription needs renewing."}}
]}, ensure_ascii=False, indent=2)

KATHETER_EN = (
    HEAD_TEMPLATE.format(
        lang="en",
        title="ISC catheters on prescription: coverage, ordering and stock tracking",
        desc="How ISC catheters are prescribed in Germany, what insurance covers, what the prescription needs and how to track your stock.",
        canonical="https://blaseunddarm.de/en/catheter-prescription.html",
        href_de="https://blaseunddarm.de/katheter-rezept.html",
        href_en="https://blaseunddarm.de/en/catheter-prescription.html",
        og_title="ISC catheters on prescription",
        og_desc="Coverage, ordering and stock tracking — explained clearly.",
        og_locale="en_GB",
        jsonld=f'<script type="application/ld+json">\n{KR_JSONLD_EN}\n</script>\n<script type="application/ld+json">\n{KR_FAQ_EN}\n</script>',
    )
    + "\n" + masthead_en("/katheter-rezept.html") + """

<main id="main">

  <section class="wrap" style="padding-block: clamp(3rem,8vw,5rem) 0">
    <p class="eyebrow">Reference</p>
    <h1 style="font-family:var(--display);font-weight:300;font-size:clamp(2.2rem,1.5rem+3.4vw,4rem);line-height:1.06;letter-spacing:-.02em;margin:0 0 1.5rem;max-width:20ch">Catheters on prescription — and always enough in stock.</h1>
    <p class="lede">If you self-catheterise, you need supplies every day. In Germany, statutory insurance covers the cost — but the prescription must be right, and stock must last. This page explains the process from doctor to delivery.</p>
  </section>

  <section class="section wrap"><div class="measure">
    <h2>Who pays for ISC catheters?</h2>
    <p>ISC catheters are classified as medical aids (Hilfsmittel). With a doctor's prescription, statutory health insurance covers the cost in full — minus the legal co-payment (up to 10 euros per month unless exempt). Private insurance terms vary.</p>
    <p>Supply runs through licensed medical suppliers — for example PubliCare, GHD or Manfred Sauer. They also provide guidance and training.</p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>What the prescription needs</h2>
    <p>A medical aid prescription for ISC catheters requires:</p>
    <ul>
      <li><strong>Box 7</strong> (Hilfsmittel) ticked</li>
      <li><strong>Diagnosis</strong> — e.g. "neurogenic bladder dysfunction due to spinal cord injury"</li>
      <li><strong>Product name and manufacturer</strong> — e.g. "Coloplast SpeediCath Compact Set"</li>
      <li><strong>Charrière size</strong> and tip type if relevant (Nelaton, Tiemann)</li>
      <li><strong>Quantity per day</strong> and <strong>prescription period</strong> — e.g. "6×/day, 3 months"</li>
    </ul>
    <div class="hinweis"><p><strong>Tip: tick aut idem.</strong> When this field is marked, the supplier must deliver exactly the prescribed product. Without it, they may substitute a "comparable" product — which does not always fit.</p></div>
    <p>In addition to catheters, accessories can be prescribed: urine bags, gloves, and — under an OTC exception — antiseptics (e.g. Octenisept) and lubricants for catheterisation.</p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Standing prescriptions</h2>
    <p>If the need is stable, the doctor can issue a standing prescription (Dauerverordnung). The supplier submits it to the insurer; once approved, it applies until revoked. This saves doctor visits — but if requirements change, a new prescription is needed.</p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Keeping track of stock</h2>
    <p>Six catheters a day, three months' supply — that is 540 units. Sounds like a lot; it runs out faster than expected. Without counting, you may find yourself without catheters on a weekend.</p>
    <p>The <a href="/en/">Bladder &amp; Bowel Manager</a> app solves this: every catheterisation subtracts one, remaining days are displayed and a warning fires in time. If you use more than one catheter type, both stocks are tracked. Since version 4.13, the package scanner reads barcodes and labels — name, Charrière and material are filled in automatically.</p>
  </div></section>

  <section class="section wrap"><div class="measure">
    <h2>Related pages</h2>
    <p><a href="/en/intermittent-catheterisation.html">ISC guide</a> · <a href="/en/uti-neurogenic-bladder.html">Recognise a UTI</a> · <a href="/en/fluid-intake.html">Fluid Intake</a> · <a href="/en/">The app</a></p>
  </div></section>
"""
    + sources_en([
        ("German medical aids directive (Hilfsmittel-Richtlinie, § 92 SGB V)", ""),
        ("Catheter prescription guide (Selbsthilfeverband Inkontinenz)", "https://www.selbsthilfeverband-inkontinenz.org/svi_suite/svisuite/tipps_katheter_rezept.php"),
    ])
    + AUTHOR_EN + "\n</main>\n\n" + footer_en("/katheter-rezept.html")
)

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

SITEMAP_ENTRIES = """  <url><loc>https://blaseunddarm.de/darmmanagement.html</loc><priority>0.9</priority></url>
  <url><loc>https://blaseunddarm.de/en/bowel-management.html</loc><priority>0.7</priority></url>
  <url><loc>https://blaseunddarm.de/katheter-rezept.html</loc><priority>0.9</priority></url>
  <url><loc>https://blaseunddarm.de/en/catheter-prescription.html</loc><priority>0.7</priority></url>"""

def run():
    os.chdir(ROOT)
    print("═══ Neue Seiten ═══")

    for fn, content in [
        ("darmmanagement.html", DARM_DE),
        ("en/bowel-management.html", DARM_EN),
        ("katheter-rezept.html", KATHETER_DE),
        ("en/catheter-prescription.html", KATHETER_EN),
    ]:
        p = ROOT / fn
        if not p.exists():
            safe_write(p, content)
        else:
            print(f"  ⏭  {fn} existiert bereits")

    # Sitemap
    print("\n═══ Sitemap ═══")
    sm = ROOT / "sitemap.xml"
    text = sm.read_text("utf-8")
    if "darmmanagement" not in text:
        text = text.replace("</urlset>", SITEMAP_ENTRIES + "\n</urlset>")
        sm.write_text(text, "utf-8")
        print("  ✅ 4 URLs ergänzt")
    else:
        print("  ⏭  bereits vorhanden")

    # Update Wissen-Pillar with new topics
    print("\n═══ Wissen-Pillar aktualisieren ═══")
    wissen = ROOT / "wissen.html"
    if wissen.exists():
        wt = wissen.read_text("utf-8")
        if "darmmanagement" not in wt:
            insert = """
      <div class="topic">
        <h3><a href="/darmmanagement.html">Darmmanagement bei Querschnittlähmung</a></h3>
        <p>Reflexiver und schlaffer Darm, Abführrhythmus, Ernährung und warum Dokumentation hilft.</p>
      </div>

      <div class="topic">
        <h3><a href="/katheter-rezept.html">Katheter auf Rezept: Verordnung und Bestand</a></h3>
        <p>Wie ISK-Katheter verordnet werden, was die Kasse zahlt und wie man den Bestand im Griff behält.</p>
      </div>
"""
            anchor = '      <div class="topic">\n        <h3><a href="/autonome-dysreflexie.html">'
            if anchor in wt:
                wt = wt.replace(anchor, insert + "\n" + anchor)
                wissen.write_text(wt, "utf-8")
                print("  ✅ wissen.html: 2 Themen ergänzt")
            else:
                ERRORS.append("wissen.html: Anker für Einfügung nicht gefunden")

    wissen_en = ROOT / "en" / "knowledge.html"
    if wissen_en.exists():
        wt = wissen_en.read_text("utf-8")
        if "bowel-management" not in wt:
            insert = """
      <div class="topic">
        <h3><a href="/en/bowel-management.html">Bowel Management with SCI</a></h3>
        <p>Reflex and flaccid bowel, bowel routine, diet and why documentation helps.</p>
      </div>

      <div class="topic">
        <h3><a href="/en/catheter-prescription.html">Catheters on Prescription: Coverage and Stock</a></h3>
        <p>How ISC catheters are prescribed in Germany, what insurance covers and how to track your stock.</p>
      </div>
"""
            anchor = '      <div class="topic">\n        <h3><a href="/en/autonomic-dysreflexia.html">'
            if anchor in wt:
                wt = wt.replace(anchor, insert + "\n" + anchor)
                wissen_en.write_text(wt, "utf-8")
                print("  ✅ en/knowledge.html: 2 topics added")
            else:
                ERRORS.append("en/knowledge.html: anchor not found")

    # Update Wissen page heading count
    for wp in [wissen, wissen_en]:
        if wp.exists():
            t = wp.read_text("utf-8")
            if "Sieben Ratgeber" in t:
                t = t.replace("Sieben Ratgeber", "Neun Ratgeber")
                wp.write_text(t, "utf-8")
                print(f"  ✅ {wp.name}: Sieben→Neun")
            if "Seven guides" in t:
                t = t.replace("Seven guides", "Nine guides")
                wp.write_text(t, "utf-8")
                print(f"  ✅ {wp.name}: Seven→Nine")

    print(f"\n{'='*50}")
    if ERRORS:
        print(f"⚠️  {len(ERRORS)} Probleme:")
        for e in ERRORS:
            print(f"   • {e}")
    else:
        print("✅ Alle Änderungen fehlerfrei.")
    print(f"\nDeploy:")
    print(f"  cd /var/www/blaseunddarm && python3 seo-seiten-3.py")
    print(f'  git add -A && git commit -m "SEO: Darmmanagement + Katheter-Rezept" && git push')

if __name__ == "__main__":
    run()
