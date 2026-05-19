import csv
import io
import json
import os
import tempfile
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .forms import DynamicFormModelForm, FieldFormSet, PublicDynamicForm
from .models import DynamicForm, FormField, FormSubmission, FormAnswer


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def form_detail(request, slug):
    form_obj = get_object_or_404(DynamicForm, slug=slug)
    if not form_obj.is_active and not request.user.is_staff:
        raise Http404('هذا الفورم غير متاح حاليًا')
    public_form = PublicDynamicForm(request.POST or None, form_instance=form_obj)
    if request.method == 'POST' and public_form.is_valid():
        submission = FormSubmission.objects.create(
            form=form_obj,
            ip_address=client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
        )
        for name, value in public_form.cleaned_data.items():
            field = public_form.fields[name].form_field_obj
            FormAnswer.objects.create(
                submission=submission,
                field=field,
                field_label=field.label,
                value=str(value) if value is not None else '',
            )
        return render(request, 'smartforms/success.html', {'form_obj': form_obj})
    return render(request, 'smartforms/public_form.html', {'form_obj': form_obj, 'public_form': public_form})


def home(request):
    first_form = DynamicForm.objects.filter(is_active=True).order_by('created_at').first()
    if first_form:
        return redirect(first_form.get_absolute_url())
    return render(request, 'smartforms/empty_home.html')

def robots_txt(request):
    base = f'{request.scheme}://{request.get_host()}'
    content = '\n'.join([
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        f'Sitemap: {base}/sitemap.xml',
        '',
    ])
    return HttpResponse(content, content_type='text/plain; charset=utf-8')

def sitemap_xml(request):
    base = f'{request.scheme}://{request.get_host()}'
    urls = [(f'{base}/', None)]
    for form_obj in DynamicForm.objects.filter(is_active=True).only('slug', 'updated_at'):
        urls.append((f'{base}{form_obj.get_absolute_url()}', form_obj.updated_at))
    parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        parts.append('<url>')
        parts.append(f'<loc>{loc}</loc>')
        if lastmod:
            parts.append(f'<lastmod>{lastmod.date().isoformat()}</lastmod>')
        parts.append('</url>')
    parts.append('</urlset>')
    return HttpResponse('\n'.join(parts), content_type='application/xml; charset=utf-8')

def admin_changelist_url(model):
    return reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist")

@staff_member_required
def dashboard(request):
    forms = DynamicForm.objects.annotate(total_submissions=Count('submissions')).order_by('-created_at')
    latest_submissions = FormSubmission.objects.select_related('form').prefetch_related('answers')[:8]
    stats = {
        'forms_count': DynamicForm.objects.count(),
        'active_forms_count': DynamicForm.objects.filter(is_active=True).count(),
        'submissions_count': FormSubmission.objects.count(),
        'fields_count': FormField.objects.count(),
    }
    user_model = get_user_model()
    admin_links = {
        'index': reverse('admin:index'),
        'users': admin_changelist_url(user_model),
        'forms': admin_changelist_url(DynamicForm),
        'fields': admin_changelist_url(FormField),
        'submissions': admin_changelist_url(FormSubmission),
    }
    return render(
        request,
        'smartforms/dashboard.html',
        {
            'forms': forms,
            'latest_submissions': latest_submissions,
            'stats': stats,
            'admin_links': admin_links,
        },
    )

@staff_member_required
def export_backup_json(request):
    if request.method != 'GET':
        raise Http404()
    buf = io.StringIO()
    call_command('dumpdata', '--indent', '2', stdout=buf)
    filename = timezone.now().strftime('backup_%Y%m%d_%H%M%S.json')
    response = HttpResponse(buf.getvalue(), content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@staff_member_required
def import_backup_json(request):
    if request.method != 'POST':
        raise Http404()
    uploaded = request.FILES.get('backup_json')
    if not uploaded:
        messages.error(request, 'ارفع ملف JSON أولاً.')
        return redirect('dashboard')
    raw_bytes = uploaded.read()
    try:
        raw_text = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raw_text = raw_bytes.decode('utf-8-sig', errors='replace')
    try:
        json.loads(raw_text)
    except json.JSONDecodeError:
        messages.error(request, 'الملف مش JSON صحيح.')
        return redirect('dashboard')

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8')
    tmp.write(raw_text)
    tmp.close()

    try:
        call_command('flush', '--noinput')
        call_command('loaddata', tmp.name)
    except Exception as exc:
        return HttpResponse(
            f'<h2>حصل خطأ أثناء الاستيراد</h2><pre>{str(exc)}</pre><p><a href="/dashboard/">رجوع للداشبورد</a></p>',
            content_type='text/html; charset=utf-8',
            status=500,
        )
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

    return HttpResponse(
        '<h2>تم استيراد النسخة الاحتياطية بنجاح</h2>'
        '<p>ملاحظة: الاستيراد عمل Reset كامل للداتابيز، فممكن تحتاج تعمل تسجيل دخول تاني.</p>'
        '<p><a href="/admin/login/">تسجيل الدخول</a> | <a href="/dashboard/">الداشبورد</a></p>',
        content_type='text/html; charset=utf-8',
    )

@staff_member_required
def form_toggle_active(request, pk):
    if request.method != 'POST':
        raise Http404()
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    form_obj.is_active = not form_obj.is_active
    form_obj.save(update_fields=['is_active'])
    messages.success(request, 'تم تحديث حالة الفورم.')
    return redirect('dashboard')

@staff_member_required
def form_delete(request, pk):
    if request.method != 'POST':
        raise Http404()
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    title = form_obj.title
    form_obj.delete()
    messages.success(request, f'تم حذف الفورم: {title}')
    return redirect('dashboard')

@staff_member_required
def form_create(request):
    if request.method == 'POST':
        form = DynamicFormModelForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, 'تم إنشاء الفورم. أضف الأسئلة الآن.')
            return redirect('dashboard_form_edit', pk=obj.pk)
    else:
        form = DynamicFormModelForm(initial={'submit_button_text': 'إرسال البيانات'})
    return render(request, 'smartforms/form_builder.html', {'builder_form': form, 'form_obj': None})

@staff_member_required
def form_edit(request, pk):
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    qs = form_obj.fields.all()
    if request.method == 'POST':
        builder_form = DynamicFormModelForm(request.POST, instance=form_obj)
        formset = FieldFormSet(request.POST, queryset=qs, prefix='fields')
        if builder_form.is_valid() and formset.is_valid():
            builder_form.save()
            fields = formset.save(commit=False)
            for deleted in formset.deleted_objects:
                deleted.delete()
            for field in fields:
                field.form = form_obj
                field.save()
            messages.success(request, 'تم حفظ التعديلات.')
            return redirect('dashboard_form_edit', pk=form_obj.pk)
    else:
        builder_form = DynamicFormModelForm(instance=form_obj)
        formset = FieldFormSet(queryset=qs, prefix='fields')
    return render(request, 'smartforms/form_builder.html', {'builder_form': builder_form, 'formset': formset, 'form_obj': form_obj})

@staff_member_required
def field_add(request, pk):
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    next_order = (form_obj.fields.order_by('-order').first().order + 1) if form_obj.fields.exists() else 1
    FormField.objects.create(form=form_obj, label='سؤال جديد', field_type='text', order=next_order)
    messages.success(request, 'تم إضافة سؤال جديد.')
    return redirect('dashboard_form_edit', pk=form_obj.pk)

@staff_member_required
def submissions_list(request, pk):
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    submissions = form_obj.submissions.prefetch_related('answers')
    return render(request, 'smartforms/submissions.html', {'form_obj': form_obj, 'submissions': submissions})

@staff_member_required
def submission_delete(request, pk, submission_id):
    if request.method != 'POST':
        raise Http404()
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    submission = get_object_or_404(FormSubmission, pk=submission_id, form=form_obj)
    submission.delete()
    messages.success(request, 'تم حذف الرد.')
    return redirect('dashboard_submissions', pk=form_obj.pk)

@staff_member_required
def export_submissions_csv(request, pk):
    form_obj = get_object_or_404(DynamicForm, pk=pk)
    fields = list(form_obj.fields.all())
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{form_obj.slug}_submissions.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['ID', 'تاريخ الإرسال'] + [field.label for field in fields])
    for submission in form_obj.submissions.prefetch_related('answers'):
        answer_map = {answer.field_id: answer.value for answer in submission.answers.all()}
        writer.writerow([submission.id, submission.created_at.strftime('%Y-%m-%d %H:%M')] + [answer_map.get(field.id, '') for field in fields])
    return response
