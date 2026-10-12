"""Find Creative Commons photos for a route and download candidates for the gallery.

Runs on GitHub Actions (the build container cannot reach these sites). Reads
tools/photo-requests/<route>.json:
  {"queries": ["Mailbox Peak"], "categories": ["Mailbox Peak"],
   "points": [[lat, lon, radius_m], ...], "max": 80}
Writes tools/photo-candidates/<route>/NNN.jpg (1024 px) and meta.json with title,
author, licence and source page for each, for the gallery and the credits.
"""
import json, os, re, sys, time, urllib.parse, urllib.request, html

UA = 'HikePlannerPhotoSearch/1.0 (https://github.com/ellokojavi/enchantments)'
OK = re.compile(r'^(cc0|pdm|public domain|cc[- ]by(-sa)?[- ]\d|cc[- ]by(-sa)?$|by(-sa)?$)', re.I)

def get(url):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            print('retry', url[:100], e, file=sys.stderr); time.sleep(2 ** i)
    return None

def commons(params):
    q = dict(params, format='json', formatversion='2')
    b = get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q))
    return json.loads(b) if b else {}

def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

def commons_files(req):
    titles = []
    for c in req.get('categories', []):
        for depth_cat in [c]:
            r = commons({'action': 'query', 'list': 'categorymembers', 'cmtitle': 'Category:' + depth_cat,
                         'cmtype': 'file', 'cmlimit': '200'})
            titles += [m['title'] for m in r.get('query', {}).get('categorymembers', [])]
    for q in req.get('queries', []):
        r = commons({'action': 'query', 'list': 'search', 'srsearch': q, 'srnamespace': '6', 'srlimit': '100'})
        titles += [m['title'] for m in r.get('query', {}).get('search', [])]
    for lat, lon, rad in req.get('points', []):
        r = commons({'action': 'query', 'list': 'geosearch', 'gscoord': f'{lat}|{lon}', 'gsradius': str(min(10000, rad)),
                     'gsnamespace': '6', 'gslimit': '200'})
        titles += [m['title'] for m in r.get('query', {}).get('geosearch', [])]
    titles = [t for t in dict.fromkeys(titles) if re.search(r'\.(jpe?g|png|webp|tiff?)$', t, re.I)]
    out = []
    for i in range(0, len(titles), 40):
        r = commons({'action': 'query', 'prop': 'imageinfo|coordinates', 'titles': '|'.join(titles[i:i + 40]),
                     'iiprop': 'url|extmetadata|size', 'iiurlwidth': '1024'})
        for p in r.get('query', {}).get('pages', []):
            ii = (p.get('imageinfo') or [{}])[0]; em = ii.get('extmetadata', {})
            lic = strip(em.get('LicenseShortName', {}).get('value'))
            if not OK.search(lic) and 'public domain' not in lic.lower():
                print('skip licence', p['title'], lic, file=sys.stderr); continue
            co = (p.get('coordinates') or [{}])[0]
            out.append(dict(source='Wikimedia Commons', title=p['title'][5:], thumb=ii.get('thumburl'),
                            page=ii.get('descriptionurl'), author=strip(em.get('Artist', {}).get('value')) or 'unknown',
                            license=lic, license_url=em.get('LicenseUrl', {}).get('value', ''),
                            desc=strip(em.get('ImageDescription', {}).get('value'))[:300],
                            date=strip(em.get('DateTimeOriginal', {}).get('value'))[:20],
                            lat=co.get('lat'), lon=co.get('lon'), w=ii.get('width'), h=ii.get('height')))
    return out

def openverse(req):
    out = []
    for q in req.get('queries', []):
        b = get('https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(
            {'q': q, 'page_size': '50', 'license_type': 'commercial,modification', 'mature': 'false'}))
        if not b: continue
        for r in json.loads(b).get('results', []):
            if r.get('source') == 'wikimedia': continue          # already covered, with better metadata
            out.append(dict(source=r.get('source', 'openverse').capitalize(), title=r.get('title') or '',
                            thumb=r.get('url'), page=r.get('foreign_landing_url'), author=r.get('creator') or 'unknown',
                            license=('CC ' + r.get('license', '').upper() + ' ' + (r.get('license_version') or '')).strip(),
                            license_url=r.get('license_url', ''), desc='', date='', lat=None, lon=None,
                            w=r.get('width'), h=r.get('height')))
    return out

def main(route):
    req = json.load(open(f'tools/photo-requests/{route}.json'))
    cands = commons_files(req) + openverse(req)
    seen = set(); keep = []
    for c in cands:
        if not c['thumb'] or c['thumb'] in seen: continue
        seen.add(c['thumb']); keep.append(c)
    keep = keep[:req.get('max', 80)]
    d = f'tools/photo-candidates/{route}'; os.makedirs(d, exist_ok=True)
    meta = []
    for i, c in enumerate(keep):
        b = get(c['thumb'])
        if not b or len(b) < 5000: continue
        fn = f'{i:03d}.jpg'; open(f'{d}/{fn}', 'wb').write(b)
        meta.append(dict(c, file=fn))
    json.dump(meta, open(f'{d}/meta.json', 'w'), indent=1, ensure_ascii=False)
    print(route, len(cands), 'found,', len(meta), 'downloaded')

if __name__ == '__main__':
    for r in sys.argv[1:]: main(r)
