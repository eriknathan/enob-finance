from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_months', '0004_remove_fixedexpense_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialmonth',
            name='opening_balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
