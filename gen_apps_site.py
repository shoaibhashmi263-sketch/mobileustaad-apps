#!/usr/bin/env python3
"""Generate the apps.mobileustaad.com static site.

Reads assets/data/apps.json, writes index.html, categories/, apps/, guides/,
robots.txt and sitemap.xml. Official Play Store links only — never APKs.
"""
import json, os, html as h

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE_DIR, 'site')
DATA = json.load(open(os.path.join(BASE_DIR, 'assets/data/apps.json'), encoding='utf-8'))
BASE = 'https://apps.mobileustaad.com'
MAIN = 'https://mobileustaad.com'

STYLE = """<style>
*{box-sizing:border-box}body{font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;margin:0;background:#0b1020;color:#e8ecf5;line-height:1.6}
.wrap{max-width:860px;margin:0 auto;padding:20px 16px 60px}
a{color:#7dd3fc}.back{display:inline-block;margin:18px 0;color:#a5b4fc;text-decoration:none}
h1{font-size:1.6rem;margin:.4em 0}h2{font-size:1.25rem;margin:1.2em 0 .5em}
.hero{text-align:center;padding:30px 10px}
.hero h1{font-size:2rem}.tag{color:#9aa3b2;max-width:560px;margin:0 auto}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin:16px 0}
.card{background:#141b31;border:1px solid #1e2742;border-radius:12px;padding:16px 12px;text-decoration:none;color:#e8ecf5;display:block;text-align:center}
.card:hover{border-color:#7dd3fc}.card .ic{font-size:2.2rem}.card b{display:block;margin-top:8px;font-size:.92rem}
.card .d{color:#9aa3b2;font-size:.78rem;margin-top:4px}
.appic{width:72px;height:72px;border-radius:18px;background:linear-gradient(135deg,#1e3a8a,#7c3aed);display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:700;color:#fff;margin:10px 0}
img.appic{width:72px;height:72px;border-radius:18px;margin:10px 0;object-fit:cover;display:block;background:none}
.card img.icimg{width:44px;height:44px;border-radius:11px;object-fit:cover;display:block;margin:0 auto}
.btn{display:inline-block;background:#16a34a;color:#fff;font-weight:700;padding:12px 26px;border-radius:10px;text-decoration:none;margin:14px 0}
.btn:hover{background:#15803d}
.feat{background:#141b31;border:1px solid #1e2742;border-radius:10px;padding:4px 18px;margin:16px 0}
.feat li{margin:.5em 0}
.warn{background:#3a2b12;border:1px solid #b45309;border-radius:10px;padding:12px 14px;margin:16px 0;font-size:.9rem}
.meta{color:#9aa3b2;font-size:.85rem}
footer{margin-top:36px;color:#6b7280;font-size:.8rem;border-top:1px solid #1e2742;padding-top:16px}
.cathead{display:flex;align-items:center;gap:12px}.cathead .ic{font-size:2.4rem}
ol.steps li{margin:.7em 0}
@media(max-width:560px){.grid{grid-template-columns:repeat(2,1fr)}}
</style>"""

def head(title, desc, canon, og_img=None):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{h.escape(title)}</title>
<meta name="description" content="{h.escape(desc)}" />
<link rel="canonical" href="{canon}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{h.escape(title)}" />
<meta property="og:description" content="{h.escape(desc)}" />
<meta property="og:url" content="{canon}" />
{STYLE}
</head>
<body>
<div class="wrap">
<a class="back" href="{BASE}/">📱 App Ustaad</a> <span class="meta">· by <a href="{MAIN}/">Mobile Ustaad</a></span>
"""

FOOT = f"""<footer><p>App Ustaad · Safe Android apps for Pakistan · All downloads via official Google Play Store links only. We never host APK files.</p></footer>
</div>
</body>
</html>"""

def _icon_file(slug):
    return os.path.join(SITE, 'assets', 'app-icons', slug + '.png')

def app_icon(name, slug):
    # Official app icon when available (user feedback 2026-10-13: no fake-looking tiles)
    if os.path.exists(_icon_file(slug)):
        return f'<img class="appic" src="/assets/app-icons/{h.escape(slug)}.png" alt="{h.escape(name)} icon" loading="lazy" />'
    return f'<div class="appic">{h.escape(name[0].upper())}</div>'

def card_icon(a, fallback_emoji):
    # Official app icon on cards when available, else the emoji fallback
    if os.path.exists(_icon_file(a['slug'])):
        return f'<img class="icimg" src="/assets/app-icons/{h.escape(a["slug"])}.png" alt="{h.escape(a["name"])}" loading="lazy" />'
    return h.escape(fallback_emoji)

def play_url(pkg):
    return f'https://play.google.com/store/apps/details?id={pkg}'

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)

def home(apps, cats, guides):
    cat_by_slug = {c['slug']: c for c in cats}
    cards = ''.join(
        f'<a class="card" href="{BASE}/apps/{a["slug"]}/"><div class="ic">{card_icon(a, cat_by_slug[a["category"]]["icon"])}</div><b>{h.escape(a["name"])}</b><div class="d">{h.escape(a["developer"])}</div></a>'
        for a in apps)
    catcards = ''.join(
        f'<a class="card" href="{BASE}/categories/{c["slug"]}/"><div class="ic">{c["icon"]}</div><b>{h.escape(c["name"])}</b><div class="d">{h.escape(c["description"][:60])}…</div></a>'
        for c in cats)
    gcards = ''.join(
        f'<a class="card" href="{BASE}/guides/{g["slug"]}/"><div class="ic">📖</div><b>{h.escape(g["title"])}</b><div class="d">{h.escape(g["excerpt"])}</div></a>'
        for g in guides)
    return (head('Best Android Apps in Pakistan 2026 | App Ustaad',
                 'Safe, reviewed Android apps for Pakistan — games, video editors, finance apps and more. Official Play Store links only.',
                 BASE + '/') +
        f'<div class="hero"><h1>📱 App Ustaad</h1><p class="tag">Hand-picked Android apps for Pakistan — reviewed, safe, and linked only to the official Google Play Store. No APKs, ever.</p></div>'
        f'<h2>Categories</h2><div class="grid">{catcards}</div>'
        f'<h2>Featured Apps</h2><div class="grid">{cards}</div>'
        f'<h2>Guides</h2><div class="grid">{gcards}</div>' + FOOT)

def category_page(c, apps):
    cards = ''.join(
        f'<a class="card" href="{BASE}/apps/{a["slug"]}/"><div class="ic">{card_icon(a, "📲")}</div><b>{h.escape(a["name"])}</b><div class="d">{h.escape(a["developer"])}</div></a>'
        for a in apps if a['category'] == c['slug'])
    return (head(f'{c["name"]} Apps in Pakistan | App Ustaad', c['description'], f'{BASE}/categories/{c["slug"]}/') +
        f'<div class="cathead"><div class="ic">{c["icon"]}</div><h1>{h.escape(c["name"])} Apps</h1></div><p class="tag">{h.escape(c["description"])}</p>'
        f'<div class="grid">{cards}</div>' + FOOT)

def app_page(a, cats):
    c = next(x for x in cats if x['slug'] == a['category'])
    feats = ''.join(f'<li>{h.escape(f)}</li>' for f in a['features'])
    ld = {"@context": "https://schema.org", "@type": "MobileApplication",
          "name": a['name'], "operatingSystem": "Android",
          "applicationCategory": c['name'], "author": {"@type": "Organization", "name": a['developer']},
          "url": f'{BASE}/apps/{a["slug"]}/',
          "installUrl": play_url(a['package'])}
    og = f'<meta property="og:image" content="{BASE}/assets/app-icons/{h.escape(a["slug"])}.png" />\n' if os.path.exists(_icon_file(a['slug'])) else ''
    return (head(f'{a["name"]} for Android — Review & Download | App Ustaad',
                 f'{a["name"]} by {a["developer"]}: review, features and official Google Play Store download link for Pakistan.',
                 f'{BASE}/apps/{a["slug"]}/')
        .replace('</head>', f'{og}<script type="application/ld+json">{json.dumps(ld)}</script>\n</head>') +
        f'{app_icon(a["name"], a["slug"])}<h1>{h.escape(a["name"])}</h1>'
        f'<p class="meta">By {h.escape(a["developer"])} · Category: <a href="{BASE}/categories/{c["slug"]}/">{h.escape(c["name"])}</a></p>'
        f'<p>{h.escape(a["review"])}</p>'
        f'<div class="feat"><ul>{feats}</ul></div>'
        f'<a class="btn" href="{play_url(a["package"])}" rel="noopener">⬇ Get it on Google Play</a>'
        f'<div class="warn">Always download from the official Play Store link above. Never install APK files from random websites.</div>' + FOOT)

def guide_page(g):
    steps = ''.join(f'<li>{h.escape(x.strip())}</li>' for x in g['content'].split('\n') if x.strip())
    return (head(f'{g["title"]} | App Ustaad', g['excerpt'], f'{BASE}/guides/{g["slug"]}/') +
        f'<h1>{h.escape(g["title"])}</h1><p class="tag">{h.escape(g["excerpt"])}</p>'
        f'<ol class="steps">{steps}</ol>' + FOOT)

def main():
    apps, cats, guides = DATA['apps'], DATA['categories'], DATA['guides']
    write(f'{SITE}/index.html', home(apps, cats, guides))
    for c in cats:
        write(f'{SITE}/categories/{c["slug"]}/index.html', category_page(c, apps))
    for a in apps:
        write(f'{SITE}/apps/{a["slug"]}/index.html', app_page(a, cats))
    for g in guides:
        write(f'{SITE}/guides/{g["slug"]}/index.html', guide_page(g))
    urls = [BASE + '/'] + [f'{BASE}/categories/{c["slug"]}/' for c in cats] + \
           [f'{BASE}/apps/{a["slug"]}/' for a in apps] + [f'{BASE}/guides/{g["slug"]}/' for g in guides]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         ''.join(f'  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>\n' for u in urls) + '</urlset>'
    write(f'{SITE}/sitemap.xml', sm)
    write(f'{SITE}/robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    print(f'wrote {len(urls)} pages')

if __name__ == '__main__':
    main()
