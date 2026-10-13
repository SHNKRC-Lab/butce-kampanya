# Bütçe · kampanya listesi

Bütçe uygulamasının indirdiği **imzalı** banka kampanyaları listesi. Kişisel veri içermez.

- `campaigns.json` — kampanyalar (banka, kart, kapsadığı abonelikler, fayda, bitiş tarihi, resmi bağlantı)
- `campaigns.json.sig` — Ed25519 imzası. Uygulama imzayı içindeki açık anahtarla doğrular; tutmazsa listeyi kullanmaz.

`campaigns.json` her güncellendiğinde GitHub Actions listeyi denetler (`tools/check.py`: şema, uzunluklar,
yalnızca izinli banka alan adlarına bağlantı) ve geçerse imzalar. Gizli anahtar depoda değil,
depo ayarlarındaki `KAMPANYA_ANAHTAR` sırrındadır.

Koşullar bankalara aittir ve değişebilir; liste bilgi amaçlıdır.
