# Generated manually for the smart forms starter project.
from django.db import migrations, models
import django.db.models.deletion


def seed_dahab_form(apps, schema_editor):
    DynamicForm = apps.get_model('smartforms', 'DynamicForm')
    FormField = apps.get_model('smartforms', 'FormField')
    form = DynamicForm.objects.create(
        title='حجز رحلة دهب',
        description='سجل بياناتك الأساسية، ولو معاك مرافقين ضيفهم في الملاحظات أو استخدم فورم مرافقين منفصل عند الحاجة.',
        slug='dahab-trip',
        submit_button_text='تسجيل الحجز المبدئي',
        success_message='تم تسجيل بيانات الحجز بنجاح، وسيتم التواصل معك لتأكيد الحجز.',
        note='تسجيل البيانات لا يعني تأكيد الحجز، ويتم التأكيد بعد التواصل معك من فريق التنظيم.',
        is_active=True,
    )
    fields = [
        ('الاسم', 'text', 'اكتب الاسم بالكامل', '', '', True, 1),
        ('النوع', 'radio', '', '', 'ذكر\nأنثى', True, 2),
        ('رقم التليفون / واتساب', 'phone', 'مثال: 01000000000', '', '', True, 3),
        ('السن', 'number', 'مثال: 24', '', '', True, 4),
        ('المرافقين والملاحظات', 'textarea', 'مثال: معايا أحمد - صديق، سارة - أخت', 'اكتب أي مرافقين معاك والعلاقة بيهم أو أي ملاحظات مهمة.', '', False, 5),
    ]
    for label, field_type, placeholder, help_text, choices, is_required, order in fields:
        FormField.objects.create(form=form, label=label, field_type=field_type, placeholder=placeholder, help_text=help_text, choices=choices, is_required=is_required, order=order)


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='DynamicForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160, verbose_name='اسم الفورم')),
                ('description', models.TextField(blank=True, verbose_name='وصف مختصر')),
                ('slug', models.SlugField(blank=True, help_text='اتركه فارغًا وسيتم إنشاء لينك عشوائي.', max_length=80, unique=True, verbose_name='لينك الفورم')),
                ('is_active', models.BooleanField(default=True, verbose_name='مفعل')),
                ('submit_button_text', models.CharField(default='إرسال البيانات', max_length=80, verbose_name='نص زر الإرسال')),
                ('success_message', models.TextField(default='تم تسجيل البيانات بنجاح، وسيتم التواصل معك قريبًا.', verbose_name='رسالة النجاح')),
                ('note', models.TextField(blank=True, verbose_name='ملاحظة تظهر آخر الفورم')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'فورم', 'verbose_name_plural': 'الفورمز', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=180, verbose_name='عنوان السؤال')),
                ('field_type', models.CharField(choices=[('text', 'نص قصير'), ('phone', 'رقم تليفون'), ('number', 'رقم'), ('email', 'بريد إلكتروني'), ('textarea', 'نص طويل'), ('select', 'قائمة اختيار'), ('radio', 'اختيار واحد'), ('checkbox', 'مربع اختيار'), ('date', 'تاريخ')], default='text', max_length=20, verbose_name='نوع السؤال')),
                ('placeholder', models.CharField(blank=True, max_length=180, verbose_name='Placeholder')),
                ('help_text', models.CharField(blank=True, max_length=220, verbose_name='مساعدة صغيرة')),
                ('choices', models.TextField(blank=True, help_text='لو السؤال اختيار: اكتب كل اختيار في سطر.', verbose_name='الاختيارات')),
                ('is_required', models.BooleanField(default=True, verbose_name='إجباري')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='الترتيب')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='smartforms.dynamicform')),
            ],
            options={'verbose_name': 'سؤال', 'verbose_name_plural': 'أسئلة الفورم', 'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='smartforms.dynamicform')),
            ],
            options={'verbose_name': 'رد', 'verbose_name_plural': 'الردود', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='FormAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_label', models.CharField(max_length=180)),
                ('value', models.TextField(blank=True)),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='smartforms.formfield')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='smartforms.formsubmission')),
            ],
            options={'verbose_name': 'إجابة', 'verbose_name_plural': 'الإجابات'},
        ),
        migrations.RunPython(seed_dahab_form, migrations.RunPython.noop),
    ]
