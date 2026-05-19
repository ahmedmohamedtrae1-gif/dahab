# Smart Forms System - Django

سيستم فورمز عام باللغة العربية، مناسب للموبايل واللابتوب، وفيه فورم جاهز مبدئي لرحلة دهب.

## المميزات

- إنشاء عدد غير محدود من الفورمز.
- لكل فورم لينك مستقل مثل: `/f/dahab-trip/`.
- تقدر تختار لينك مخصص من الداشبورد أو تسيبه يتولد تلقائيًا.
- تفعيل/إغلاق أي فورم.
- بناء الأسئلة من الداشبورد.
- أنواع أسئلة متعددة:
  - نص قصير
  - رقم تليفون
  - رقم
  - بريد إلكتروني
  - نص طويل
  - قائمة اختيار
  - اختيار واحد
  - Checkbox
  - تاريخ
- حفظ الردود في قاعدة البيانات.
- عرض الردود من الداشبورد.
- تصدير الردود CSV.
- Django Admin كامل لإدارة متقدمة.
- تصميم عربي RTL، Mobile-first، وشكله مناسب للموبايل واللابتوب.

## التشغيل

```bash
cd dahab_forms_system_v2
python -m venv venv
source venv/bin/activate  # على Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## الروابط

- أول فورم مفعل: `http://127.0.0.1:8000/`
- فورم دهب الجاهز: `http://127.0.0.1:8000/f/dahab-trip/`
- الداشبورد: `http://127.0.0.1:8000/dashboard/`
- Django Admin: `http://127.0.0.1:8000/admin/`

## طريقة استخدام الداشبورد

1. اعمل superuser وشغل السيرفر.
2. افتح `/dashboard/`.
3. اضغط `+ فورم جديد`.
4. اكتب اسم الفورم، الوصف، ورسالة النجاح.
5. اكتب slug مخصص مثل `summer-trip` أو سيبه فاضي.
6. بعد إنشاء الفورم، اضغط `إضافة سؤال`.
7. عدل السؤال، النوع، هل إجباري، والترتيب.
8. لو السؤال اختيار، اكتب الاختيارات كل اختيار في سطر.
9. افتح لينك الفورم وشاركه مع الناس.

## ملاحظات إنتاجية مهمة

قبل رفعه Production:

- غير `SECRET_KEY` في `form_system/settings.py`.
- خلي `DEBUG = False`.
- حدد `ALLOWED_HOSTS` بدومين الموقع.
- استخدم PostgreSQL بدل SQLite لو الاستخدام كبير.
- شغل `python manage.py collectstatic`.
