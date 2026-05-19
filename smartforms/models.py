import secrets
import string
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

ARABIC_SLUG_MAP = str.maketrans({
    'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي', 'ء': ''
})

def random_slug(length=8):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def make_slug(value):
    raw = (value or '').strip().lower().translate(ARABIC_SLUG_MAP)
    candidate = slugify(raw, allow_unicode=False)
    return candidate or random_slug()

class DynamicForm(models.Model):
    title = models.CharField('اسم الفورم', max_length=160)
    description = models.TextField('وصف مختصر', blank=True)
    slug = models.SlugField('لينك الفورم', max_length=80, unique=True, blank=True, help_text='اتركه فارغًا وسيتم إنشاء لينك عشوائي.')
    is_active = models.BooleanField('مفعل', default=True)
    submit_button_text = models.CharField('نص زر الإرسال', max_length=80, default='إرسال البيانات')
    success_message = models.TextField('رسالة النجاح', default='تم تسجيل البيانات بنجاح، وسيتم التواصل معك قريبًا.')
    note = models.TextField('ملاحظة تظهر آخر الفورم', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'فورم'
        verbose_name_plural = 'الفورمز'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = make_slug(self.title)
            slug = base
            i = 2
            while DynamicForm.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}' if base else random_slug()
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('form_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class FormField(models.Model):
    TEXT = 'text'
    PHONE = 'phone'
    NUMBER = 'number'
    EMAIL = 'email'
    TEXTAREA = 'textarea'
    SELECT = 'select'
    RADIO = 'radio'
    CHECKBOX = 'checkbox'
    DATE = 'date'
    COMPANIONS = 'companions'
    FIELD_TYPES = [
        (TEXT, 'نص قصير'),
        (PHONE, 'رقم تليفون'),
        (NUMBER, 'رقم'),
        (EMAIL, 'بريد إلكتروني'),
        (TEXTAREA, 'نص طويل'),
        (SELECT, 'قائمة اختيار'),
        (RADIO, 'اختيار واحد'),
        (CHECKBOX, 'مربع اختيار'),
        (DATE, 'تاريخ'),
        (COMPANIONS, 'مرافقين (حجز جماعي)'),
    ]

    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField('عنوان السؤال', max_length=180)
    field_type = models.CharField('نوع السؤال', max_length=20, choices=FIELD_TYPES, default=TEXT)
    placeholder = models.CharField('Placeholder', max_length=180, blank=True)
    help_text = models.CharField('مساعدة صغيرة', max_length=220, blank=True)
    choices = models.TextField('الاختيارات', blank=True, help_text='لو السؤال اختيار: اكتب كل اختيار في سطر.')
    is_required = models.BooleanField('إجباري', default=True)
    order = models.PositiveIntegerField('الترتيب', default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'سؤال'
        verbose_name_plural = 'أسئلة الفورم'

    def choice_list(self):
        return [line.strip() for line in self.choices.splitlines() if line.strip()]

    def __str__(self):
        return f'{self.form.title} - {self.label}'

class FormSubmission(models.Model):
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='submissions')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'رد'
        verbose_name_plural = 'الردود'

    def __str__(self):
        return f'{self.form.title} #{self.id}'

class FormAnswer(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='answers')
    field = models.ForeignKey(FormField, on_delete=models.SET_NULL, blank=True, null=True)
    field_label = models.CharField(max_length=180)
    value = models.TextField(blank=True)

    class Meta:
        verbose_name = 'إجابة'
        verbose_name_plural = 'الإجابات'

    def __str__(self):
        return f'{self.field_label}: {self.value[:50]}'
