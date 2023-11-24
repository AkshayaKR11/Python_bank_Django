# Generated by Django 4.2.6 on 2023-10-27 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account_management', '0003_alter_account_account_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('deposit', 'deposit'), ('withdraw', 'withdraw')], default='deposit', max_length=8)),
                ('transaction_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='account_management.account')),
            ],
        ),
    ]