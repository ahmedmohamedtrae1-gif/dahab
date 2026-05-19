from django.db import migrations


def seed_companions_field(apps, schema_editor):
    DynamicForm = apps.get_model('smartforms', 'DynamicForm')
    FormField = apps.get_model('smartforms', 'FormField')

    form = DynamicForm.objects.filter(slug='dahab-trip').first()
    if not form:
        return

    exists = FormField.objects.filter(form_id=form.id, field_type='companions').exists()
    if exists:
        return

    last = FormField.objects.filter(form_id=form.id).order_by('-order').first()
    next_order = (last.order + 1) if last else 1

    FormField.objects.create(
        form_id=form.id,
        label='بيانات المرافقين',
        field_type='companions',
        help_text='اضغط إضافة مرافق لكل شخص، واكتب بياناته + صلة القرابة بالنسبة للي حاجز.',
        is_required=False,
        order=next_order,
    )


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('smartforms', '0002_alter_formfield_field_type'),
    ]

    operations = [
        migrations.RunPython(seed_companions_field, reverse_code=noop),
    ]

