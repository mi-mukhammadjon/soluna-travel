from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=200)          # modeltranslation orqali ko'p tilga
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='regions/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        return self.name


class Attraction(models.Model):
    """Har bir regiondagi mashhur joylar"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='attractions')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='attractions/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Достопримечательность'
        verbose_name_plural = 'Достопримечательностей'

    def __str__(self):
        return f"{self.region.name} - {self.name}"
