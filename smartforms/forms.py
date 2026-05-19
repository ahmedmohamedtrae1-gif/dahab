import json
from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import DynamicForm, FormField

class DynamicFormModelForm(forms.ModelForm):
    class Meta:
        model = DynamicForm
        fields = ['title', 'description', 'slug', 'is_active', 'submit_button_text', 'success_message', 'note']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'success_message': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

class FormFieldModelForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ['label', 'field_type', 'placeholder', 'help_text', 'choices', 'is_required', 'order']
        widgets = {
            'choices': forms.Textarea(attrs={'rows': 3, 'placeholder': 'صديق\nأب\nأم'}),
        }

FieldFormSet = modelformset_factory(FormField, form=FormFieldModelForm, extra=0, can_delete=True)

class PublicDynamicForm(forms.Form):
    def __init__(self, *args, form_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_instance = form_instance
        self._companions_field_names = []
        for field in form_instance.fields.all():
            kwargs = {
                'label': field.label,
                'required': field.is_required,
                'help_text': field.help_text,
            }
            widget_attrs = {'placeholder': field.placeholder, 'class': 'input'}
            name = f'field_{field.id}'
            if field.field_type == FormField.COMPANIONS:
                self._companions_field_names.append(name)
                companions_kwargs = dict(kwargs)
                companions_kwargs.pop('required', None)
                self.fields[name] = forms.CharField(
                    required=False,
                    widget=forms.HiddenInput(attrs={'data-companions-input': '1'}),
                    **companions_kwargs,
                )
                self.fields[name].form_field_obj = field
                continue
            if field.field_type == FormField.TEXTAREA:
                self.fields[name] = forms.CharField(widget=forms.Textarea(attrs={**widget_attrs, 'rows': 4}), **kwargs)
            elif field.field_type == FormField.NUMBER:
                self.fields[name] = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs=widget_attrs), **kwargs)
            elif field.field_type == FormField.PHONE:
                self.fields[name] = forms.CharField(widget=forms.TextInput(attrs={**widget_attrs, 'inputmode': 'tel'}), **kwargs)
            elif field.field_type == FormField.EMAIL:
                self.fields[name] = forms.EmailField(widget=forms.EmailInput(attrs=widget_attrs), **kwargs)
            elif field.field_type == FormField.DATE:
                self.fields[name] = forms.DateField(widget=forms.DateInput(attrs={**widget_attrs, 'type': 'date'}), **kwargs)
            elif field.field_type in [FormField.SELECT, FormField.RADIO]:
                choices = [('', 'اختر')] + [(c, c) for c in field.choice_list()]
                widget = forms.RadioSelect(attrs={'class': 'choice-list'}) if field.field_type == FormField.RADIO else forms.Select(attrs={'class': 'input'})
                self.fields[name] = forms.ChoiceField(choices=choices, widget=widget, **kwargs)
            elif field.field_type == FormField.CHECKBOX:
                self.fields[name] = forms.BooleanField(required=False, label=field.label, help_text=field.help_text)
            else:
                self.fields[name] = forms.CharField(widget=forms.TextInput(attrs=widget_attrs), **kwargs)
            self.fields[name].form_field_obj = field

    def clean(self):
        cleaned_data = super().clean()
        for name in getattr(self, '_companions_field_names', []):
            form_field_obj = self.fields[name].form_field_obj
            raw = cleaned_data.get(name, '')
            if not raw:
                companions = []
            else:
                try:
                    companions = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValidationError({name: 'بيانات المرافقين غير صحيحة'}) from exc
            if companions is None:
                companions = []
            if not isinstance(companions, list):
                raise ValidationError({name: 'بيانات المرافقين غير صحيحة'})
            normalized = []
            for item in companions:
                if not isinstance(item, dict):
                    continue
                normalized_item = {
                    'name': str(item.get('name', '')).strip(),
                    'gender': str(item.get('gender', '')).strip(),
                    'phone': str(item.get('phone', '')).strip(),
                    'age': str(item.get('age', '')).strip(),
                    'notes': str(item.get('notes', '')).strip(),
                    'relation': str(item.get('relation', '')).strip(),
                    'relation_other': str(item.get('relation_other', '')).strip(),
                }
                if not normalized_item['name']:
                    continue
                normalized.append(normalized_item)
            if form_field_obj.is_required and not normalized:
                raise ValidationError({name: 'أضف بيانات مرافق واحد على الأقل'})
            cleaned_data[name] = json.dumps(normalized, ensure_ascii=False)
        return cleaned_data
