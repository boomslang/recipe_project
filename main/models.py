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



admin.site.register(UserProfile)

import datetime


class recipeClass1(models.Model):
   # recipeID =  models.AutoField(primary_key = True)
    recipeName = models.CharField(max_length=100)
    recipeDesc = models.CharField(max_length=1000)

    creatorID = models.ForeignKey(User, blank=True, null=True)
     #creatorID = models.IntegerField(default=1)

    creationDateTime = models.DateTimeField(default=datetime.date.today)

    def __unicode__(self):
        return self.recipeName

class recipeForm(forms.Form):
    recipeName = forms.CharField(max_length=100)
    recipeDesc = forms.CharField(max_length=1000, widget=forms.Textarea)
    #creatorID = forms.ModelChoiceField(queryset=UserProfile.objects.all())

admin.site.register(recipeClass1)


class ingredient2(models.Model):
   # ingredientID =  models.AutoField(primary_key = True)
    ingredientName = models.CharField(max_length=100)

    def __unicode__(self):
        return self.ingredientName

class ingredient2_form(forms.Form):
    ingredientName = forms.CharField(max_length=100)


admin.site.register(ingredient2)

class measurementUnit2(models.Model):
    #measurementUnitID =  models.AutoField(primary_key = True)
    measurementUnitName = models.CharField(max_length=100)

    def __unicode__(self):
        return self.measurementUnitName

class measurement2_form(forms.Form):
    measurementUnitName = forms.CharField(max_length=100)

admin.site.register(measurementUnit2)


class recipeContent2(models.Model):
    #recipeContentsID =  models.AutoField(primary_key = True)
    recipeID = models.ForeignKey(recipeClass1, blank=False, null=False)
    ingredientID = models.ForeignKey(ingredient2, blank=False, null=False)
    measurementUnitID = models.ForeignKey(measurementUnit2, blank=False, null=False)
    quantity = models.FloatField(default=0)

    #def __unicode__(self):
     #   return self.quantity

class recipeContents_form(forms.Form):
    #recipeID = forms.IntegerField(initial=1)
    quantity = forms.FloatField(initial=0)
    measurementUnitID = forms.ModelChoiceField(queryset=measurementUnit2.objects.all(), initial=1)

    ingredientID = forms.ModelChoiceField(queryset=ingredient2.objects.all())


admin.site.register(recipeContent2)