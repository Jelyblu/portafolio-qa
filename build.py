#!/usr/bin/env python3
"""Genera es/index.html, en/index.html e index.html a partir de content/*.json.

El texto sale palabra por palabra del PDF del portafolio (content/es.json).
content/en.json es su traducción. El diseño copia el de la página de perfil de
Dragonark Studios: styles.css es la hoja del sitio tal cual, y el CSS de abajo
es el bloque propio de esa página, con dos añadidos para la galería de capturas.

Uso:  python3 build.py
"""
import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).parent

# Datos de contacto. Un solo sitio para cambiarlos.
NOMBRE = "Angelina Builes"
CORREO = "AngelinaBuilesC@gmail.com"
TELEFONO_VISIBLE = "301 371 35 18"
TELEFONO_ENLACE = "+573013713518"
URL_BASE = "https://jelyblu.github.io/portafolio-qa"

# Proyectos cuyas capturas secundarias son pantallas de teléfono en vertical.
MOVIL = {"lupa", "mythpets", "babyfresh", "bubblehero"}

CAPTURAS = {
    "trident": 2, "ecovilla": 2, "dominos": 1, "roadtest": 2, "glitch": 2, "guesswho": 1, "babyfresh": 2, "bubblehero": 4, "interactivehome": 2, "metau": 4, "rooftop": 4,
    "lupa": 5, "80s": 3, "mythpets": 5,
}

UI = {
    "es": {"otro": "en", "otro_nombre": "English", "contacto": "Contacto",
           "captura": "captura", "cerrar": "Cerrar video", "contactame": "Contáctame",
           "estudio": "Portafolio del estudio", "estudio_url": "https://dragonarkstudios.com/es/portfolio",
           "otro_portafolio": "Portafolio de desarrollo", "otro_portafolio_url": "https://jelyblu.github.io/portafolio-dev/es/"},
    "en": {"otro": "es", "otro_nombre": "Español", "contacto": "Contact",
           "captura": "screenshot", "cerrar": "Close video", "contactame": "Contact me",
           "estudio": "Studio portfolio", "estudio_url": "https://dragonarkstudios.com/portfolio",
           "otro_portafolio": "Dev portfolio", "otro_portafolio_url": "https://jelyblu.github.io/portafolio-dev/en/"},
}

CSS = r"""
        .profile-page {
            --ab-cyan: #00e5ff; --ab-ink: #e8eeff; --ab-dim: #8f9cbc; --ab-faint: #5d6a8a;
            --ab-line: rgba(255, 255, 255, .09); --ab-surface: #0e1017; --ab-raised: #12141f;
            font-family: 'Montserrat', sans-serif;
        }
        .profile-page h1, .profile-page h2, .profile-page h3 { font-family: 'Exo 2', sans-serif; }
        .ab-notch { clip-path: polygon(0 0, calc(100% - 18px) 0, 100% 18px, 100% 100%, 0 100%); }

        .ab-hero { padding: 8.5rem 0 3.5rem; }
        .ab-hero-grid { max-width: 900px; }
        .ab-eyebrow {
            font-family: 'Exo 2', sans-serif; font-size: .7rem; font-weight: 900; font-style: italic;
            text-transform: uppercase; letter-spacing: .18em; color: var(--ab-cyan); margin: 0 0 1.1rem;
        }
        .ab-name { font-size: clamp(2.6rem, 7vw, 4.4rem); font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -.02em; line-height: .95; margin: 0 0 .9rem; color: var(--ab-ink); }
        .ab-role { font-size: clamp(1rem, 2vw, 1.2rem); font-weight: 700; color: var(--ab-cyan); line-height: 1.5; margin: 0 0 .7rem; }
        .ab-meta { font-size: .88rem; color: var(--ab-faint); line-height: 1.7; margin: 0 0 1.5rem; }
        .ab-links { display: flex; flex-wrap: wrap; gap: 1.4rem 1.1rem; }

        .ab-work { padding: 3rem 0 0; }
        .ab-featured { display: grid; gap: 1.5rem; }
        .ab-feat {
            display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
            background: var(--ab-surface); border: 1px solid var(--ab-line);
            border-top: 1px solid rgba(0, 229, 255, .32);
            transition: border-color .25s ease, transform .25s ease;
            scroll-margin-top: 90px;
        }
        .ab-feat:hover { border-top-color: var(--ab-cyan); transform: translateY(-3px); }

        /* Galería: la primera captura manda, las demás van en tira debajo,
           igual que la columna de imágenes de cada página del PDF. */
        .ab-shot {
            display: grid; grid-template-rows: minmax(230px, 1fr) 120px; background: var(--ab-raised);
            border-right: 1px solid var(--ab-line); overflow: hidden;
        }
        .ab-shot a { display: block; height: 100%; overflow: hidden; }
        .ab-shot img { display: block; width: 100%; height: 100%; object-fit: cover; transition: transform .35s ease; }
        .ab-shot a:hover img { transform: scale(1.04); }
        /* La captura principal no empuja la altura: rellena lo que mida el texto.
           Sin esto una captura vertical estira la tarjeta a más de 1000 px. */
        .ab-shot-main { min-height: 0; position: relative; }
        .ab-shot-main > a { position: absolute; inset: 0; }
        .ab-shot--solo { grid-template-rows: minmax(260px, 1fr); }
        /* Proyectos de móvil: las capturas son verticales y en una tira baja
           solo se vería una franja. Se les da más alto. */
        .ab-shot--movil { grid-template-rows: minmax(200px, 1fr) 240px; }
        .ab-shot--movil .ab-shot-strip img { object-position: center top; }
        .ab-shot-strip { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: 1px; background: var(--ab-line); min-height: 0; border-top: 1px solid var(--ab-line); }

        .ab-feat-body { padding: 2rem 2.2rem; }
        .ab-feat h3 { font-size: 1.5rem; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -.01em; color: var(--ab-ink); margin: 0 0 .45rem; }
        .ab-context { font-size: .78rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--ab-cyan); margin: 0 0 1.3rem; }
        .ab-desc p { margin: 0 0 .9rem; font-size: .92rem; line-height: 1.75; color: var(--ab-dim); text-wrap: pretty; }
        .ab-label {
            font-family: 'Exo 2', sans-serif; font-size: .64rem; font-weight: 900; font-style: italic;
            text-transform: uppercase; letter-spacing: .1em; color: var(--ab-faint); margin: 1.4rem 0 .55rem;
        }
        .ab-tech { display: flex; flex-wrap: wrap; gap: .3rem; }
        .ab-tech span {
            font-family: 'JetBrains Mono', monospace; font-size: .68rem; padding: .25rem .6rem;
            border: 1px solid rgba(0, 229, 255, .26); color: var(--ab-cyan); letter-spacing: .03em;
        }
        .ab-out { display: inline-flex; gap: .35rem; margin-top: 1.3rem; margin-right: 1.4rem; color: var(--ab-ink); text-decoration: none; font-size: .84rem; font-weight: 700; border-bottom: 1px solid rgba(0, 229, 255, .4); padding-bottom: 2px; }
        .ab-out:hover { color: var(--ab-cyan); border-bottom-color: var(--ab-cyan); }

        .ab-cta { padding: 5rem 0 6rem; }
        .ab-cta-inner {
            border: 1px solid rgba(0, 229, 255, .28); border-top: 2px solid var(--ab-cyan);
            background: radial-gradient(90% 140% at 50% 0%, rgba(0, 229, 255, .1) 0%, rgba(0, 229, 255, 0) 60%), var(--ab-surface);
            padding: 3rem 2.5rem; text-align: center;
        }
        .ab-cta-inner h2 { font-size: clamp(1.7rem, 4vw, 2.4rem); font-weight: 900; font-style: italic; text-transform: uppercase; color: var(--ab-ink); margin: 0 0 .8rem; }
        .ab-cta-inner p { color: var(--ab-dim); max-width: 56ch; margin: 0 auto 2rem; line-height: 1.8; font-size: .95rem; }
        .ab-cta-inner .ab-links { justify-content: center; }

        /* Sin logo del estudio: el nombre ocupa el centro de la cabecera. */
        .logo-container .logo-text { text-transform: uppercase; font-style: italic; }

        @media (max-width: 900px) {
            .ab-feat { grid-template-columns: 1fr; }
            .ab-shot { border-right: 0; border-bottom: 1px solid var(--ab-line); }
        }
        @media (max-width: 600px) {
            .ab-hero { padding: 7rem 0 2.5rem; }
            .ab-feat-body { padding: 1.6rem 1.4rem; }
            .ab-cta-inner { padding: 2.2rem 1.4rem; }
            .ab-shot { grid-template-rows: 220px 90px; }
            .ab-shot--movil { grid-template-rows: 200px 180px; }
            .ab-shot--solo { grid-template-rows: 220px; }
            .logo-container .logo-text { font-size: 1rem; }
        }

        .ab-vmodal { width: min(92vw, 960px); margin: auto; padding: 0; border: 1px solid var(--ab-line); border-radius: 4px; background: var(--ab-raised); overflow: visible; }
        .ab-vmodal::backdrop { background: rgba(4, 8, 16, .84); backdrop-filter: blur(6px); }
        .ab-vmodal-inner { position: relative; aspect-ratio: 16 / 9; }
        .ab-vmodal iframe { display: block; width: 100%; height: 100%; border: 0; background: #000; }
        .ab-vclose { position: absolute; top: -17px; right: -17px; width: 42px; height: 42px; display: grid; place-items: center; border: 0; border-radius: 50%; background: var(--ab-cyan); color: #04121a; font-size: 1.6rem; font-weight: 700; line-height: 1; cursor: pointer; box-shadow: 0 6px 18px rgba(0, 0, 0, .55); z-index: 1; }
        .ab-vclose:hover { filter: brightness(1.12); }
        .ab-vclose:focus-visible { outline: 3px solid #fff; outline-offset: 2px; }
        @media (max-width: 560px) { .ab-vclose { top: 8px; right: 8px; } }
"""

SCRIPT = r"""
        (function () {
            // Menú: el mismo mecanismo que usa main.js en Dragonark.
            var toggle = document.querySelector('.mobile-nav-toggle');
            var nav = document.getElementById('primary-navigation');
            function setMenu(open) {
                nav.setAttribute('data-visible', open ? 'true' : 'false');
                toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            }
            toggle.addEventListener('click', function () {
                setMenu(nav.getAttribute('data-visible') !== 'true');
            });
            nav.querySelectorAll('a').forEach(function (a) {
                a.addEventListener('click', function () { setMenu(false); });
            });
            document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

            // Video en ventana: YouTube sin cookies. Sin JS, el enlace abre YouTube.
            var modal = document.getElementById('ab-vmodal');
            if (!modal || !modal.showModal) return;
            var frame = modal.querySelector('iframe');
            document.querySelectorAll('a[data-yt]').forEach(function (link) {
                link.addEventListener('click', function (e) {
                    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
                    e.preventDefault();
                    frame.src = 'https://www.youtube-nocookie.com/embed/' + link.getAttribute('data-yt') + '?autoplay=1&rel=0';
                    modal.showModal();
                });
            });
            modal.querySelector('[data-ab-vclose]').addEventListener('click', function () { modal.close(); });
            modal.addEventListener('click', function (e) { if (e.target === modal) modal.close(); });
            modal.addEventListener('close', function () { frame.src = 'about:blank'; });
        })();
"""


def e(texto):
    return html.escape(texto, quote=True)


def id_youtube(url):
    m = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', url)
    return m.group(1) if m else ""


def galeria(pid, titulo, etiqueta):
    n = CAPTURAS[pid]
    def img(k, lazy=True):
        src = f"../assets/img/{pid}-{k}.jpg"
        carga = ' loading="lazy"' if lazy else ""
        return (f'<a href="{src}" target="_blank" rel="noopener">'
                f'<img src="{src}" alt="{e(titulo)}, {etiqueta} {k}"{carga}></a>')
    tira = "".join(img(k) for k in range(2, n + 1))
    clase = "ab-shot ab-shot--movil" if pid in MOVIL else "ab-shot"
    if n == 1:
        return (f'<div class="ab-shot ab-shot--solo">\n'
                f'                            <div class="ab-shot-main">{img(1)}</div>\n'
                f'                        </div>')
    return (f'<div class="{clase}">\n'
            f'                            <div class="ab-shot-main">{img(1)}</div>\n'
            f'                            <div class="ab-shot-strip">{tira}</div>\n'
            f'                        </div>')


def proyecto(p, t, ui):
    parrafos = "\n".join(f"                                <p>{e(x)}</p>" for x in p["parrafos"])
    apps = "".join(f"<span>{e(a)}</span>" for a in p["apps"])
    enlaces = ""
    if p.get("video"):
        yt = id_youtube(p["video"])
        enlaces = (f'<a class="ab-out" href="{e(p["video"])}" data-yt="{yt}" '
                   f'target="_blank" rel="noopener">{e(t["etiquetas"]["video"])} &rarr;</a>')
    if p.get("isla"):
        enlaces += (f'<a class="ab-out" href="{e(p["isla"])}" '
                    f'target="_blank" rel="noopener">{e(t["etiquetas"]["isla"])} &rarr;</a>')
    if p.get("web"):
        enlaces += (f'\n                            <a class="ab-out" href="{e(p["web"])}" '
                    f'target="_blank" rel="noopener">{e(t["etiquetas"]["web"])} &rarr;</a>')
    for etiqueta, url in p.get("enlaces", []):
        enlaces += (f'\n                            <a class="ab-out" href="{e(url)}" '
                    f'target="_blank" rel="noopener">{e(etiqueta)} &rarr;</a>')
    if p.get("descarga"):
        enlaces += (f'\n                            <a class="ab-out" href="{e(p["descarga"])}" '
                    f'target="_blank" rel="noopener">{e(t["etiquetas"]["descarga"])} &rarr;</a>')
    return f"""
                    <article class="ab-feat" id="{p['id']}">
                        {galeria(p['id'], p['titulo'], ui['captura'])}
                        <div class="ab-feat-body">
                            <h3>{e(p['titulo'])}</h3>
                            <p class="ab-context">{e(p['tipo'])}</p>
                            <div class="ab-desc">
{parrafos}
                            </div>
                            <p class="ab-label">{e(t['etiquetas']['apps'])}</p>
                            <div class="ab-tech">{apps}</div>
                            {enlaces}
                        </div>
                    </article>"""


def abanico(n):
    """Retrasos del abanico del menú para n enlaces. Los de styles.css están
    pensados para los seis de Dragonark y dejan los demás sin orden."""
    dentro = "\n".join(
        f'        #primary-navigation[data-visible="true"] .nav-links > li:nth-child({i}) > a {{ animation-delay: {40 + 44 * (i - 1)}ms; }}'
        for i in range(1, n + 1))
    fuera = "\n".join(
        f'        #primary-navigation[data-visible="false"] .nav-links > li:nth-child({i}) > a {{ animation-delay: {28 * (n - i)}ms; }}'
        for i in range(1, n + 1))
    return "\n" + dentro + "\n" + fuera + "\n"


def pagina(lang, t):
    ui = UI[lang]
    por = t["portada"]
    linea = f"{CORREO} | {TELEFONO_VISIBLE} | {por['ciudad']}"
    menu = "\n".join(
        f'                    <li><a href="#{p["id"]}">{e(p["titulo"])}</a></li>' for p in t["proyectos"])
    proyectos = "".join(proyecto(p, t, ui) for p in t["proyectos"])
    titulos = ", ".join(p["titulo"] for p in t["proyectos"])
    descripcion = f"{por['titulo'].capitalize()} QA · {NOMBRE}. {titulos}."
    return f"""<!DOCTYPE html>
<html lang="{lang}">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{e(por['titulo'])} · {e(NOMBRE)}</title>
    <meta name="description" content="{e(descripcion)}">
    <link rel="canonical" href="{URL_BASE}/{lang}/">
    <link rel="alternate" hreflang="es" href="{URL_BASE}/es/">
    <link rel="alternate" hreflang="en" href="{URL_BASE}/en/">
    <link rel="alternate" hreflang="x-default" href="{URL_BASE}/es/">
    <meta property="og:title" content="{e(por['titulo'])} · {e(NOMBRE)}">
    <meta property="og:description" content="{e(descripcion)}">
    <meta property="og:image" content="{URL_BASE}/assets/img/trident-1.jpg">
    <meta property="og:type" content="profile">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Exo+2:ital,wght@0,400;0,700;0,900;1,700;1,900&family=Montserrat:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../styles.css">
    <style>{CSS}{abanico(len(t["proyectos"]) + 2)}    </style>
</head>

<body>
    <header id="main-header" class="scrolled">
        <div class="container nav-wrapper">
            <a href="#top" class="logo-container"><span class="logo-text">{e(NOMBRE)}</span></a>
            <button class="mobile-nav-toggle" aria-controls="primary-navigation" aria-expanded="false">
                <div class="hamburger"></div>
            </button>
            <nav id="primary-navigation">
                <ul class="nav-links">
{menu}
                    <li><a href="#contacto">{ui['contacto']}</a></li>
                    <li><a href="../{ui['otro']}/" hreflang="{ui['otro']}" lang="{ui['otro']}">{ui['otro_nombre']}</a></li>
                </ul>
            </nav>
            <a class="nav-cta" href="../{ui['otro']}/" hreflang="{ui['otro']}" lang="{ui['otro']}">{ui['otro_nombre']}</a>
        </div>
    </header>

    <main class="profile-page" id="top">
        <section class="ab-hero">
            <div class="container">
                <div class="ab-hero-grid">
                    <p class="ab-eyebrow">{e(por['subtitulo'])}</p>
                    <h1 class="ab-name">{e(NOMBRE)}</h1>
                    <p class="ab-role">{e(por['titulo'])} {e(por['anio'])}</p>
                    <p class="ab-meta">{e(linea)}</p>
                    <div class="ab-links">
                        <a class="btn btn-primary" href="mailto:{CORREO}">{ui['contactame']}</a>
                        <a class="btn btn-secondary" href="https://www.linkedin.com/in/angelinabuiles" target="_blank" rel="noopener">LinkedIn</a>
                        <a class="btn btn-secondary" href="https://github.com/Jelyblu" target="_blank" rel="noopener">GitHub</a>
                        <a class="btn btn-secondary" href="https://dragonarkstudios.itch.io" target="_blank" rel="noopener">itch.io</a>
                        <a class="btn btn-secondary" href="https://www.fiverr.com/angibuiles" target="_blank" rel="noopener">Fiverr</a>
                        <a class="btn btn-secondary" href="{ui['estudio_url']}" target="_blank" rel="noopener">{ui['estudio']}</a>
                    </div>
                </div>
            </div>
        </section>

        <section class="ab-work">
            <div class="container">
                <h2 class="sr-only">{e(por['titulo'])}</h2>
                <div class="ab-featured">{proyectos}
                </div>
            </div>
        </section>

        <section class="ab-cta" id="contacto">
            <div class="container">
                <div class="ab-cta-inner ab-notch">
                    <h2>{e(t['etiquetas']['cierre'])}</h2>
                    <p>{e(linea)}</p>
                    <div class="ab-links">
                        <a class="btn btn-primary" href="mailto:{CORREO}">{CORREO}</a>
                        <a class="btn btn-secondary" href="tel:{TELEFONO_ENLACE}">{TELEFONO_VISIBLE}</a>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="footer-bottom">
            <p>{e(linea)}</p>
        </div>
    </footer>

    <dialog id="ab-vmodal" class="ab-vmodal">
        <div class="ab-vmodal-inner">
            <button type="button" class="ab-vclose" data-ab-vclose>
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">{ui['cerrar']}</span>
            </button>
            <iframe title="Video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
        </div>
    </dialog>

    <script>{SCRIPT}    </script>
</body>

</html>
"""


RAIZ_HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{e(NOMBRE)}</title>
    <link rel="canonical" href="{URL_BASE}/es/">
    <meta http-equiv="refresh" content="0; url=es/">
    <script>
        // Inglés a quien tenga el navegador en inglés; español al resto.
        location.replace(/^en\\b/i.test(navigator.language || '') ? 'en/' : 'es/');
    </script>
</head>
<body>
    <p><a href="es/">Español</a> · <a href="en/">English</a></p>
</body>
</html>
"""


def main():
    for lang in ("es", "en"):
        t = json.loads((RAIZ / "content" / f"{lang}.json").read_text(encoding="utf-8"))
        (RAIZ / lang / "index.html").write_text(pagina(lang, t), encoding="utf-8")
    (RAIZ / "index.html").write_text(RAIZ_HTML, encoding="utf-8")
    print("Generado: index.html, es/index.html, en/index.html")


if __name__ == "__main__":
    main()
