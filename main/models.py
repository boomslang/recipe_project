
from django.contrib.auth.models import User, UserManager
from django.db import models
from django import forms
from django.contrib import admin
from django.forms import ModelForm
import datetime

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

class Recipe(models.Model):
    recipeName = models.CharField(max_length=100, unique=True)
    recipeDesc = models.CharField(max_length=1000)

    creator = models.ForeignKey(User, blank=True, null=True)
    num_likes = models.IntegerField(default = 0)

    creationDateTime = models.DateTimeField(default=datetime.date.today)

    def __unicode__(self):
        return self.recipeName

class RecipeForm(ModelForm):
    #class Meta:
     #   model = Recipe
    recipeName = forms.CharField(max_length=100)
    recipeDesc = forms.CharField(max_length=1000, widget=forms.Textarea)
    #creator = forms.ModelChoiceField(queryset=UserProfile.objects.all())


class Ingredient(models.Model):
    ingredientName = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.ingredientName

# class IngredientForm(ModelForm):
#     class Meta:
#         model = Ingredient
#     ingredientName = forms.CharField(max_length=100)




class MeasurementUnit(models.Model):
    measurementUnitName = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.measurementUnitName


# class measurement2_form(ModelForm):
#     class Meta:
#         model = MeasurementUnit
#     measurementUnitName = forms.CharField(max_length=100)




class RecipeContent(models.Model):
    #recipeContentsID =  models.AutoField(primary_key = True)
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredient)
    measurementUnit = models.ForeignKey(MeasurementUnit)
    quantity = models.FloatField(default=0)

    def __unicode__(self):
        return str(self.id) + " - " + self.recipe.recipeName + " - " + self.ingredient.ingredientName

class RecipeContentForm(ModelForm):
    class Meta:
        model = RecipeContent
        exclude = ('recipe',)
    quantity = forms.FloatField(initial=0)
    measurementUnit = forms.ModelChoiceField(queryset=MeasurementUnit.objects.all(), initial=1)
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all())


class Like(models.Model):
    user = models.ForeignKey(User, blank=False, null=False)
    recipe = models.ForeignKey(Recipe, blank=False, null=False)
    def __unicode__(self):
        return self.user.username + " - "  + self.recipe.recipeName

class Tag(models.Model):
    description = models.CharField(max_length=20, primary_key=True)
    def __unicode__(self):
        return self.description

class TagForm(forms.Form):
    description = forms.CharField(max_length=20)

class UserTagRecipe(models.Model):
    user = models.ForeignKey(User, blank=False, null=False)
    recipe = models.ForeignKey(Recipe, blank=False, null=False)
    tag = models.ForeignKey(Tag ,blank=False, null=False )
    def __unicode__(self):
        return self.user.username + " - "  + self.tag.description + " - "  + self.recipe.recipeName

class Mutate(models.Model):
    user = models.ForeignKey(User, blank=False, null=False)
    source_recipe = models.ForeignKey(Recipe, related_name="s+")
    mutated_recipe = models.ForeignKey(Recipe, related_name="m+")

    def __unicode__(self):
        return self.user.username + " - " + self.source_recipe.recipeName + " - " + self.mutated_recipe.recipeName

class ReplacedIngredients(models.Model):
    original_ingredient = models.ForeignKey(Ingredient, related_name="first+")
    replaced_ingredient = models.ForeignKey(Ingredient, related_name="second+")
    count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.original_ingredient.ingredientName + " - " + self.replaced_ingredient.ingredientName

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100,required=True, help_text='Search for recipes!')

admin.site.register(UserProfile)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeContent)
admin.site.register(MeasurementUnit)
admin.site.register(ReplacedIngredients)
admin.site.register(Mutate)
admin.site.register(Like)
admin.site.register(Tag)
admin.site.register(UserTagRecipe)
