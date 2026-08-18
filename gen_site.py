# -*- coding: utf-8 -*-
"""Genera dos páginas (soporte y privacidad) con los tres idiomas adentro.
El idioma se cambia en la página, sin recargar: una sola URL para cada una."""
import pathlib, html, json, runpy

OUT = pathlib.Path("/tmp/yugidb-site")
LANGS = ["es", "en", "pt"]
NAMES = {"es": "ES", "en": "EN", "pt": "PT"}
HTMLLANG = {"es": "es", "en": "en", "pt": "pt-BR"}

T = json.loads(pathlib.Path("/tmp/strings.json").read_text(encoding="utf-8"))

def block(lang, kind):
    t = T[lang]
    if kind == "support":
        faq = "".join(f'<div class="card"><h3>{html.escape(q)}</h3><p>{a}</p></div>' for q, a in t["faq"])
        return (f'<h1>{t["h1"]}</h1><p>{t["intro"]}</p>'
                f'<h2>{t["contact_h"]}</h2><p>{t["contact_p"]}</p>'
                f'<h2>{t["faq_h"]}</h2>{faq}'
                f'<footer><p>{t["foot1"]}</p><p>{t["foot2"]}</p></footer>')
    table = ("<table><tr><th>" + "</th><th>".join(t["t_head"]) + "</th></tr>"
             + "".join(f"<tr><td><code>{s}</code></td><td>{p}</td></tr>" for s, p in t["t_rows"])
             + "</table>")
    lst = "<ul>" + "".join(f"<li>{x}</li>" for x in t["nots"]) + "</ul>"
    secs = []
    for head, paras in t["p_sections"]:
        secs.append(f"<h2>{head}</h2>")
        for p in paras:
            secs.append(table if p == "TABLE" else lst if p == "LIST" else f"<p>{p}</p>")
    return (f'<h1>{t["p_h1"]}</h1><p class="upd">{t["p_updated"]}</p>' + "".join(secs)
            + f'<footer><p>{t["foot2"]}</p></footer>')

SCRIPT = """
<script>
(function(){
  var LANGS=%s, TITLES=%s, NAV=%s;
  function pick(){
    try{ var s=localStorage.getItem('yugidb-lang'); if(LANGS.indexOf(s)>-1) return s; }catch(e){}
    var prefs=navigator.languages||[navigator.language||'es'];
    for(var i=0;i<prefs.length;i++){
      var c=String(prefs[i]).slice(0,2).toLowerCase();
      if(LANGS.indexOf(c)>-1) return c;
    }
    return 'en';                     // lo que no hablamos cae en inglés, igual que la app
  }
  function apply(l){
    LANGS.forEach(function(x){
      document.querySelectorAll('[data-lang="'+x+'"]').forEach(function(n){
        n.hidden = (x!==l);
      });
    });
    document.querySelectorAll('.lg').forEach(function(b){
      b.classList.toggle('on', b.dataset.set===l);
      b.setAttribute('aria-pressed', b.dataset.set===l);
    });
    document.documentElement.lang = ({es:'es',en:'en',pt:'pt-BR'})[l];
    document.title = TITLES[l];
    var nav = document.querySelectorAll('nav a');
    if(nav.length===2){ nav[0].textContent=NAV[l][0]; nav[1].textContent=NAV[l][1]; }
    try{ localStorage.setItem('yugidb-lang', l); }catch(e){}
  }
  document.addEventListener('click', function(e){
    var b=e.target.closest('.lg'); if(!b) return;
    e.preventDefault(); apply(b.dataset.set);
  });
  apply(pick());
})();
</script>
"""

for kind, fname in (("support", "index.html"), ("privacy", "privacy.html")):
    titles = {l: T[l]["support_title" if kind == "support" else "privacy_title"] for l in LANGS}
    nav = {l: [T[l]["nav_support"], T[l]["nav_privacy"]] for l in LANGS}
    langs_btns = "".join(
        f'<button class="lg{" on" if l=="es" else ""}" data-set="{l}" aria-pressed="{str(l=="es").lower()}">{NAMES[l]}</button>'
        for l in LANGS)
    # Sin JS se ve el español; el script decide el resto al cargar.
    blocks = "".join(
        f'<div data-lang="{l}"{"" if l=="es" else " hidden"}>{block(l, kind)}</div>' for l in LANGS)
    page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titles['es']}</title><link rel="stylesheet" href="style.css?v=3"></head><body>
<div class="wrap">
<header><div class="topline"><div class="logo">YUGI<span>DB</span></div>
<div class="langs">{langs_btns}</div></div>
<nav><a href="index.html">{T['es']['nav_support']}</a><a href="privacy.html">{T['es']['nav_privacy']}</a></nav></header>
{blocks}
</div>{SCRIPT % (json.dumps(LANGS), json.dumps(titles, ensure_ascii=False), json.dumps(nav, ensure_ascii=False))}
</body></html>"""
    (OUT / fname).write_text(page, encoding="utf-8")

for extra in ["index.en.html", "index.pt.html", "privacy.en.html", "privacy.pt.html"]:
    p = OUT / extra
    if p.exists(): p.unlink()

print("generadas:", ", ".join(sorted(p.name for p in OUT.glob("*.html"))))
