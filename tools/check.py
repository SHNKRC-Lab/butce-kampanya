#!/usr/bin/env python3
"""Kampanya listesini imzalamadan önce denetler. Hata varsa liste İMZALANMAZ.

Uygulamadaki doğrulamanın (lib/data/campaign_feed.dart) aynısı + daha katı kurallar:
şema, uzunluklar, tarih biçimi, tekrar eden kimlik ve bağlantıların yalnızca izinli
banka alan adlarına gitmesi (oltalama bağlantısı listeye giremez).
"""
import json
import re
import sys
from datetime import date
from urllib.parse import urlparse

ALLOWED_HOSTS = {
    'enpara.com', 'teb.com.tr', 'cepteteb.com.tr', 'kartavantaj.com',
    'axess.com.tr', 'akbank.com', 'bonus.com.tr', 'garantibbva.com.tr', 'paraf.com.tr', 'halkbank.com.tr',
    'maximum.com.tr', 'isbank.com.tr', 'qnbcard.com.tr', 'qnb.com.tr', 'vakifkart.com.tr',
    'vakifbank.com.tr', 'worldcard.com.tr', 'yapikredi.com.tr', 'bankkart.com.tr', 'ziraatbank.com.tr',
    'burgan.com.tr', 'hayatfinans.com.tr', 'denizbank.com', 'kuveytturk.com.tr',
}
LIMITS = {'bank': 60, 'title': 140, 'benefit': 140, 'detail': 600, 'product': 60}
ID = re.compile(r'^[a-z0-9-]{1,60}$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
CTRL = re.compile(r'[\x00-\x1f\x7f]')


def fail(msg):
    print(f'HATA: {msg}')
    sys.exit(1)


def url_ok(u):
    p = urlparse(u)
    if p.scheme != 'https' or p.port or p.username or p.password:
        return False
    h = (p.hostname or '').lower()
    return any(h == a or h.endswith('.' + a) for a in ALLOWED_HOSTS)


def main(path):
    raw = open(path, 'rb').read()
    if len(raw) > 512 * 1024:
        fail('dosya 512 KB sınırını aşıyor')
    d = json.loads(raw.decode('utf-8'))
    if d.get('version') != 1:
        fail('version 1 olmalı')
    for k in ('generatedAt', 'checkedAt'):
        v = d.get(k)
        if not isinstance(v, str) or not DATE.match(v):
            fail(f'{k} YYYY-AA-GG olmalı')
        date.fromisoformat(v)
    cs = d.get('campaigns')
    if not isinstance(cs, list) or not cs or len(cs) > 300:
        fail('campaigns 1–300 öğeli liste olmalı')
    seen = set()
    for i, c in enumerate(cs):
        where = f'kampanya #{i} ({c.get("id")})'
        if not isinstance(c, dict):
            fail(f'{where}: nesne değil')
        if not isinstance(c.get('id'), str) or not ID.match(c['id']):
            fail(f'{where}: id geçersiz')
        if c['id'] in seen:
            fail(f'{where}: id tekrar ediyor')
        seen.add(c['id'])
        for k, n in LIMITS.items():
            v = c.get(k, '')
            if not isinstance(v, str) or len(v) > n or CTRL.search(v):
                fail(f'{where}: {k} metin olmalı, en fazla {n} karakter')
        for k in ('bank', 'title', 'benefit'):
            if not c.get(k, '').strip():
                fail(f'{where}: {k} boş')
        for k, n, m in (('brands', 30, 60), ('match', 10, 40), ('refund', 10, 80)):
            v = c.get(k, [])
            if not isinstance(v, list) or len(v) > n or any(not isinstance(x, str) or not x or len(x) > m for x in v):
                fail(f'{where}: {k} listesi geçersiz')
        if c.get('need', 'kart') not in ('kart', 'hesap', 'yok'):
            fail(f'{where}: need kart/hesap/yok olmalı')
        if not isinstance(c.get('join', False), bool):
            fail(f'{where}: join true/false olmalı')
        until = c.get('until', '')
        if until:
            if not DATE.match(until):
                fail(f'{where}: until YYYY-AA-GG olmalı')
            date.fromisoformat(until)
        src = c.get('source', '')
        if src and not url_ok(src):
            fail(f'{where}: bağlantı izinli bir banka sitesine gitmiyor: {src}')
        extra = set(c) - {'id', 'bank', 'title', 'benefit', 'detail', 'brands', 'need', 'until',
                          'source', 'join', 'refund', 'product', 'match'}
        if extra:
            fail(f'{where}: bilinmeyen alan(lar): {sorted(extra)}')
    print(f'Tamam: {len(cs)} kampanya, son kontrol {d["checkedAt"]}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'campaigns.json')
