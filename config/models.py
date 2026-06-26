from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField('Sayt nomi', max_length=100, default='SoLuna')
    site_tagline = models.CharField('Slogan', max_length=200, default='Your Gateway to Extraordinary Adventures')

    phone_1 = models.CharField('Telefon 1', max_length=20, default='+998 99 895 35 36')
    phone_2 = models.CharField('Telefon 2', max_length=20, blank=True)
    email_1 = models.EmailField('Email 1', default='solunadmc@gmail.com')
    email_2 = models.EmailField('Email 2', blank=True)

    address = models.CharField('Manzil', max_length=300, default='Tashkent, Uzbekistan')
    work_hours = models.CharField('Ish vaqti', max_length=100, default='8:00 – 18:00, Mon – Sat')

    instagram = models.URLField('Instagram', blank=True, default='https://instagram.com/Oygul.axatova')
    telegram = models.URLField('Telegram', blank=True, default='https://t.me/soluna_uz')
    whatsapp = models.URLField('WhatsApp', blank=True, default='https://wa.me/998950666233')
    facebook = models.URLField('Facebook', blank=True)

    promo_text = models.CharField('Promo matn', max_length=200, default='Unlock the Magic of Travel with SoLuna')
    promo_cta_text = models.CharField('Promo tugma matni', max_length=50, default='Explore Now')
    promo_cta_url = models.URLField('Promo tugma URL', blank=True, default='/tours/')

    class Meta:
        verbose_table = 'Sayt sozlamalari'
        verbose_name = 'Sayt sozlamalari'
        verbose_name_plural = 'Sayt sozlamalari'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Faqat bitta yozuv bo'lishi kerak
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
