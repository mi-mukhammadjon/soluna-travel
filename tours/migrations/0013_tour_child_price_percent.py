# Generated manually — child_price_percent field

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0012_tour_discount_label_tour_discount_percent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='child_price_percent',
            field=models.PositiveSmallIntegerField(
                default=50,
                help_text="Bola narxi — katta odam narxining foizi (0–100). "
                          "Masalan 50 = yarim narx, 0 = bepul, 100 = to'liq narx.",
                validators=[django.core.validators.MaxValueValidator(100)],
            ),
        ),
    ]
