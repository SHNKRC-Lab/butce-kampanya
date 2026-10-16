#!/usr/bin/env python3
"""Kira artış oranı listesini imzalamadan önce denetler. Hata varsa liste İMZALANMAZ.

Kurallar: şema, ardışık aylar, makul aralık (0–150), aylar arası sıçrama en fazla 10 puan,
ileri tarihli ay yok. Uygulamadaki doğrulama (lib/data/rent.dart) bunun aynısını yapar.
"""
import json
import re
import sys
from datetime import date

MONTH = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def fail(msg):
    print(f'HATA: {msg}')
    sys.exit(1)


def nxt(ym):
    y, m = int(ym[:4]), int(ym[5:])
    return f'{y + (m == 12):04d}-{m % 12 + 1:02d}'


def main(path):
    raw = open(path, 'rb').read()
    if len(raw) > 64 * 1024:
        fail('dosya 64 KB sınırını aşıyor')
    d = json.loads(raw.decode('utf-8'))
    if d.get('version') != 1 or d.get('kind') != 'kira-tufe12':
        fail('version 1 ve kind kira-tufe12 olmalı')
    g = d.get('generatedAt')
    if not isinstance(g, str) or not DATE.match(g):
        fail('generatedAt YYYY-AA-GG olmalı')
    gen = date.fromisoformat(g)
    rates = d.get('rates')
    if not isinstance(rates, dict) or not 1 <= len(rates) <= 240:
        fail('rates 1–240 öğeli nesne olmalı')
    months = sorted(rates)
    prev = None
    for ym in months:
        if not MONTH.match(ym):
            fail(f'{ym}: ay YYYY-AA olmalı')
        v = rates[ym]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 150:
            fail(f'{ym}: oran 0–150 arası sayı olmalı')
        if prev is not None:
            if ym != nxt(prev):
                fail(f'{prev} → {ym}: aylar ardışık değil')
            if abs(v - rates[prev]) > 10:
                fail(f'{ym}: önceki aya göre 10 puandan fazla sıçrama ({rates[prev]} → {v})')
        prev = ym
    last = months[-1]
    if (int(last[:4]), int(last[5:])) > (gen.year, gen.month):
        fail(f'{last}: generatedAt ({g}) ayından ileri')
    print(f'Tamam: {len(months)} ay, son {last} = %{rates[last]}')


if __name__ == '__main__':
    main(sys.argv[1])
