# Bütçe · kampanya listesi

Bütçe uygulamasının indirdiği **imzalı** listeler: banka kampanyaları ve yasal kira artış oranları. Kişisel veri içermez.

- `campaigns.json` — kampanyalar (banka, kart, kapsadığı abonelikler, fayda, bitiş tarihi, resmi bağlantı)
- `kira.json` — TÜİK TÜFE 12 aylık ortalama değişimi; anahtar kiranın yenilendiği ay (TBK m.344 üst sınırı). `tools/check_kira.py` denetler.
- `*.sig` — Ed25519 imzaları. Uygulama imzayı içindeki açık anahtarla doğrular; tutmazsa listeyi kullanmaz.

`campaigns.json` her güncellendiğinde GitHub Actions listeyi denetler (`tools/check.py`: şema, uzunluklar,
yalnızca izinli banka alan adlarına bağlantı) ve geçerse imzalar. Gizli anahtar depoda değil,
depo ayarlarındaki `KAMPANYA_ANAHTAR` sırrındadır.

Koşullar bankalara aittir ve değişebilir; liste bilgi amaçlıdır.
