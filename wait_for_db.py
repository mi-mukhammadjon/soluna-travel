import os
import polib

locale_dir = 'locale'
for lang in os.listdir(locale_dir):
    po_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
    mo_path = po_path.replace('.po', '.mo')
    if os.path.exists(po_path):
        try:
            po = polib.pofile(po_path)
            po.save_as_mofile(mo_path)
            print(f"✅ {lang} uchun .mo fayl yaratildi.")
        except Exception as e:
            print(f"❌ {lang}da xato: {e}")