from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartforms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formfield',
            name='field_type',
            field=models.CharField(
                choices=[
                    ('text', 'نص قصير'),
                    ('phone', 'رقم تليفون'),
                    ('number', 'رقم'),
                    ('email', 'بريد إلكتروني'),
                    ('textarea', 'نص طويل'),
                    ('select', 'قائمة اختيار'),
                    ('radio', 'اختيار واحد'),
                    ('checkbox', 'مربع اختيار'),
                    ('date', 'تاريخ'),
                    ('companions', 'مرافقين (حجز جماعي)'),
                ],
                default='text',
                max_length=20,
                verbose_name='نوع السؤال',
            ),
        ),
    ]
