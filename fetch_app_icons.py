#!/usr/bin/env python3
"""Fetch official app icons from each app's Google Play Store listing.

Reads assets/data/apps.json, extracts the og:image (app icon) from each
Play Store page, downloads a 256px square PNG into site/assets/app-icons/<slug>.png.

Only square-ish images are kept (guards against feature-graphic og:images).
Apps whose icon can't be fetched keep the letter-tile fallback in the generator.

Usage: python3 fetch_app_icons.py [slug ...]   # no args = all apps missing an icon
"""
import json, os, re, sys, time, urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'assets/data/apps.json')
ICON_DIR = os.path.join(BASE_DIR, 'site', 'assets', 'app-icons')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

def fetch_icon(app):
    pkg = app['package']
    url = f'https://play.google.com/store/apps/details?id={pkg}&hl=en'
    req = urllib.request.Request(url, headers=UA)
    try:
        html = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')
    except Exception as e:
        return f'page fetch failed: {e}'
    m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if not m:
        return 'no og:image found'
    base = m.group(1).split('=')[0]  # strip googleusercontent size suffix
    icon_url = base + '=s256'
    dest = os.path.join(ICON_DIR, app['slug'] + '.png')
    tmp = dest + '.tmp'
    try:
        req2 = urllib.request.Request(icon_url, headers=UA)
        data = urllib.request.urlopen(req2, timeout=25).read()
    except Exception as e:
        return f'icon download failed: {e}'
    if len(data) < 2000:
        return f'suspiciously small ({len(data)} bytes), skipped'
    open(tmp, 'wb').write(data)
    # square check
    try:
        from PIL import Image
        im = Image.open(tmp)
        w, h = im.size
        if not (0.9 <= w / h <= 1.1) or w < 96:
            os.remove(tmp)
            return f'not a square icon ({w}x{h}), skipped'
    except ImportError:
        pass  # no PIL: accept PNG as-is
    os.replace(tmp, dest)
    return 'ok'

def main():
    os.makedirs(ICON_DIR, exist_ok=True)
    apps = json.load(open(DATA_PATH, encoding='utf-8'))['apps']
    wanted = sys.argv[1:]
    if wanted:
        apps = [a for a in apps if a['slug'] in wanted]
    else:
        apps = [a for a in apps if not os.path.exists(os.path.join(ICON_DIR, a['slug'] + '.png'))]
    print(f'{len(apps)} apps need icons')
    ok, failed = 0, []
    for i, a in enumerate(apps):
        res = fetch_icon(a)
        print(f'[{i+1}/{len(apps)}] {a["slug"]}: {res}', flush=True)
        if res == 'ok':
            ok += 1
        else:
            failed.append((a['slug'], res))
        time.sleep(1.2)  # be polite to Play Store
    print(f'\ndone: {ok} ok, {len(failed)} failed')
    for slug, why in failed:
        print(f'  FAIL {slug}: {why}')

if __name__ == '__main__':
    main()
