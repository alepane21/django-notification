# -*- coding:utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _
from django.forms.models import modelformset_factory
from .models import NoticeSetting, NoticeType, NOTICE_MEDIA

from django.forms.formsets import BaseFormSet

class NoticeSettingForm(forms.Form):
    notice_type = forms.ModelChoiceField(queryset=NoticeType.objects.all(), widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        initial = kwargs["initial"]
        self.notice_type_instance = NoticeType.objects.get(id=kwargs["initial"]["notice_type"])
        initial.update(dict([
            (n.medium, n.send) for n in NoticeSetting.objects.filter(
                user = self.user,
                notice_type = self.notice_type_instance
            )
        ]))
        if not self.user:
            raise Exception("You have to pass user instance to construct this formset!")
        super(NoticeSettingForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        if not commit:
            return
        notice_type = self.cleaned_data.pop('notice_type')
        for media_id, value in self.cleaned_data.items():
            notice_setting = NoticeSetting.objects.get(
                user = self.user,
                medium = media_id,
                notice_type = notice_type,
            )
            notice_setting.send = value
            notice_setting.save()
for media_id, media_label in NOTICE_MEDIA:
    NoticeSettingForm.base_fields[media_id] = forms.BooleanField(label=media_label, required=False)

class NoticeSettingFormSet(BaseFormSet):
    form = NoticeSettingForm
    extra = 0
    can_order = False
    can_delete = False
    max_num = 0
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, **kwargs):
        self.user = kwargs.pop("user", None)
        if not self.user:
            raise Exception("You have to pass user instance to construct this formset!")

        initial = [{"notice_type":notice_type.id} for notice_type in NoticeType.objects.all()]

        defaults = {'data': data, 'files': files, 'auto_id': auto_id, 'prefix': prefix, 'initial':initial}
        defaults.update(kwargs)
        super(NoticeSettingFormSet, self).__init__(**defaults)

    def _construct_form(self, *args, **kwargs):
        kwargs.update({"user":self.user})
        return super(NoticeSettingFormSet, self)._construct_form(*args, **kwargs)

    def save(self, commit=True):
        for form in self.forms:
            form.save()
