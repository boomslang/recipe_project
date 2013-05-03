from django.contrib.auth.models import User, UserManager
from django.db import models
from django import forms
from django.contrib import admin

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key = True)
    karma = models.IntegerField(default = 0)
    objects = UserManager()
    def __unicode__(self):
        return self.user.username

class UserForm(forms.Form):
    username = forms.CharField(max_length=10,required=True, help_text='The username you want.')
    email = forms.EmailField(required=True, help_text='Please enter your e-mail.')
    password = forms.CharField(label=(u'Password'),widget=forms.PasswordInput(render_value=False))

    def clean_email(self):
        field_data = self.cleaned_data['email']

        if not field_data:
            return ''

        u = User.objects.filter(email=field_data)
        if len(u) > 0:
            raise forms.ValidationError('This e-mail is already registered.')

        return field_data
    def clean_username(self):
        field_data = self.cleaned_data['username']

        if not field_data:
            return ''

        u = User.objects.filter(username=field_data)
        if len(u) > 0:
            raise forms.ValidationError('This username is already registered.')

        return field_data

class dummy_class(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
class dummy_form(forms.Form):
    name = forms.CharField(max_length=100)

admin.site.register(UserProfile)
admin.site.register(dummy_class)