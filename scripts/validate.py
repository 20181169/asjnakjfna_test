"""Check evidence links, publication gates, excerpts and static asset references."""
import csv
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
d = json.loads((DIST / 'data/catalog.json').read_text(encoding='utf-8'))
indexes = {}
for name in ['sources', 'evidence', 'claims', 'occupations', 'reviews']:
    indexes[name] = {x['id']: x for x in d[name]}
    assert len(indexes[name]) == len(d[name]), f'duplicate {name} IDs'
quote_counts = {}
for e in d['evidence']:
    assert e['source_id'] in indexes['sources']
    assert e['excerpt'] and e['locator']
    assert e['excerpt_sha256'] == hashlib.sha256(e['excerpt'].encode()).hexdigest()
    quote_counts[e['source_id']] = quote_counts.get(e['source_id'], 0) + len(e['excerpt'].split())
assert all(count <= 25 for count in quote_counts.values()), quote_counts
for s in d['sources']:
    assert urlparse(s['url']).scheme == 'https'
    assert s['retrieved_at'] and s['limitation'] and s['region']
for c in d['claims']:
    assert c['occupation_id'] in indexes['occupations']
    assert c['evidence_ids'] and all(e in indexes['evidence'] for e in c['evidence_ids'])
    assert c['scope'] and c['version']
    assert c['confidence'] is None or 0 <= c['confidence'] <= 1
    if c['frequency'] is not None:
        assert c['frequency']['document_count'] <= c['frequency']['corpus_document_count']
    if c['review_status'] == 'approved':
        assert any(r['id'] in c['review_ids'] and r['claim_id'] == c['id'] and r['claim_version'] == c['version'] and r['decision'] == 'approve' for r in d['reviews'])
for o in d['occupations']:
    assert o['source_id'] in indexes['sources']
    assert all(indexes['claims'][cid]['occupation_id'] == o['id'] for cid in o['claim_ids'])
    assert o['mapping_note'] and o['unknowns']
    assert o['scenario']['measures_aptitude'] is False
if d['release']['public_information_release_allowed']:
    assert d['release']['expert_review_completed'] and all(c['review_status'] == 'approved' for c in d['claims'])

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, val in attrs:
            if key not in ('href', 'src') or not val: continue
            u = urlparse(val)
            if u.scheme or not u.path: continue
            assert (DIST / unquote(u.path)).is_file(), f'missing asset {val}'
for html in DIST.glob('*.html'):
    Links().feed(html.read_text(encoding='utf-8'))
with (DIST / 'data/expert-review.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.reader(f))
    assert len(rows) == len(d['claims']) + 1
    assert all(len(row) == len(rows[0]) for row in rows)
legacy = json.loads((DIST / 'data/legacy-audit.json').read_text(encoding='utf-8'))
assert legacy['status'] == 'quarantined'
assert legacy['records'], 'original work was not imported'
assert all(r['original_document_ids'] is None for r in legacy['records'])
print(f'PASS: {len(d["occupations"])} occupations, {len(d["claims"])} evidence-linked claims, all unreviewed; local assets and CSV valid.')
print(f'Excerpt words per source: {quote_counts}')
