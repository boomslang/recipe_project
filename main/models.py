from django.contrib.auth.models import User, UserManager
from django.db import models
from django import forms
from django.contrib import admin
from django.forms import ModelForm

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

class recipeForm(ModelForm):
    recipeName = forms.CharField(max_length=100)
    recipeDesc = forms.CharField(max_length=1000, widget=forms.Textarea)
    #creatorID = forms.ModelChoiceField(queryset=UserProfile.objects.all())

admin.site.register(recipeClass1)


class ingredient2(models.Model):
   # ingredientID =  models.AutoField(primary_key = True)
    ingredientName = models.CharField(max_length=100)

    def __unicode__(self):
        return self.ingredientName

class ingredient2_form(ModelForm):
    class Meta:
        model = ingredient2
    ingredientName = forms.CharField(max_length=100)


admin.site.register(ingredient2)

class measurementUnit2(models.Model):
    #measurementUnitID =  models.AutoField(primary_key = True)
    measurementUnitName = models.CharField(max_length=100)

    def __unicode__(self):
        return self.measurementUnitName

class measurement2_form(ModelForm):
    class Meta:
        model = measurementUnit2
    measurementUnitName = forms.CharField(max_length=100)

admin.site.register(measurementUnit2)


class recipeContent2(models.Model):
    #recipeContentsID =  models.AutoField(primary_key = True)
    recipeID = models.ForeignKey(recipeClass1)
    ingredientID = models.ForeignKey(ingredient2)
    measurementUnitID = models.ForeignKey(measurementUnit2)
    quantity = models.FloatField(default=0)

    def __unicode__(self):
        return str(self.id) + " - " + self.recipeID.recipeName + " - " + self.ingredientID.ingredientName

class recipeContents_form(ModelForm):
    class Meta:
        model = recipeContent2
    #recipeID = forms.IntegerField(initial=1)
    quantity = forms.FloatField(initial=0)
    measurementUnitID = forms.ModelChoiceField(queryset=measurementUnit2.objects.all(), initial=1)

    ingredientID = forms.ModelChoiceField(queryset=ingredient2.objects.all())



admin.site.register(recipeContent2)

class Like(models.Model):
    user = models.ForeignKey(User, blank=False, null=False)
    recipe = models.ForeignKey(recipeClass1, blank=False, null=False)
    def __unicode__(self):
        return self.user.username + " - "  + self.recipe.recipeName

class Tag(models.Model):
    description = models.CharField(max_length=20, primary_key=True)
    def __unicode__(self):
        return self.description

class UserTagRecipe(models.Model):
    user = models.ForeignKey(User, blank=False, null=False)
    recipe = models.ForeignKey(recipeClass1, blank=False, null=False)
    def __unicode__(self):
        return self.user.username + " - "  + self.tag.description + " - "  + self.recipe.recipeName

class Mutate(models.Model):
    user = models.ForeignKey(User, blank=False, null=False)
    #sourceRecipe = models.ForeignKey(recipeClass1)
    #mutatedRecipe = models.ForeignKey(recipeClass1)
    sourceRecipeID = models.ForeignKey(recipeClass1, related_name="s+")
    mutatedRecipeID = models.ForeignKey(recipeClass1, related_name="m+")

    def __unicode__(self):
        return self.user.username + " - " + self.sourceRecipeID.recipeName + " - " + self.mutatedRecipeID.recipeName

class ReplacedIngredients(models.Model):
    original_ingredient = models.ForeignKey(ingredient2, related_name="first+")
    replaced_ingredient = models.ForeignKey(ingredient2, related_name="second+")
    count = models.IntegerField()

    def __unicode__(self):
        return self.original_ingredient.ingredientName + " - " + self.replaced_ingredient.ingredientName

admin.site.register(ReplacedIngredients)
admin.site.register(Mutate)
admin.site.register(Like)
admin.site.register(Tag)
admin.site.register(UserTagRecipe)
