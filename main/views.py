# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.models import UserForm, UserProfile, recipeForm, recipeClass1, recipeContent2, recipeContents_form, ingredient2, measurementUnit2
from recipe_project.settings import STATIC_URL


def mainPage_view(request):
    recipes = recipeClass1.objects.all()

    d = {"recipes": recipes, "user": request.user}
    return render_to_response('main_page.html', d)


def register(request):
    if request.method == 'POST':
        formset = UserForm(request.POST, request.FILES)
        if formset.is_valid():
            newUser = User.objects.create_user(formset.data['username'], formset.data['email'],
                                               formset.data['password'])
            custom = UserProfile(user=newUser)
            custom.user_id = newUser.id
            custom.save()
            newUser = authenticate(username=request.POST['username'], password=request.POST['password'])
            login(request, newUser)
            d = {"user": request.user}
            return render_to_response("registration/register_success.html", d)
        else:
            d = {"formset": formset}
            d.update(csrf(request))
            return render_to_response("registration/register.html", d)

    else:
        userForm = UserForm()
        d = {"formset": userForm}
        d.update(csrf(request))
        return render_to_response("registration/register.html", d)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")


@login_required
def profile_view(request):
    if request.method == 'GET':

        user_createdRecipes = recipeClass1.objects.filter(creatorID=request.user.id) #active user_id ?

        d = {"user": request.user, "createdRecipes1": user_createdRecipes}
        d.update(csrf(request))
        return render_to_response('profile.html', d)


@login_required
def create_view(request):
    if request.method == 'GET':
        recipe_form1 = recipeForm()
        #ingredient_form1 = ingredient_form()
        #measurement_form1 = measurement_form()
        recipeContents_form1 = recipeContents_form()
        recipeContents_form2 = recipeContents_form()
        recipeContents_form3 = recipeContents_form()

        d = {"user": request.user, "recipeForm1": recipe_form1, "recipeContentForm1": recipeContents_form1,
             "recipeContentForm2": recipeContents_form2, "recipeContentForm3": recipeContents_form3}
        d.update(csrf(request))
        return render_to_response('create.html', d)
    else:
        formset1 = recipeForm(request.POST, request.FILES)
        formset2 = recipeContents_form(request.POST, request.FILES)
        formset3 = recipeContents_form(request.POST, request.FILES)
        formset4 = recipeContents_form(request.POST, request.FILES)

        if formset1.is_valid():
            recipe = recipeClass1.objects.create()
            recipe.recipeName = formset1.data["recipeName"]
            recipe.recipeDesc = formset1.data["recipeDesc"]
            #  recipe.creationDateTime = formset.data["creationDateTime"]
            # t = {"user": request.user}
            #c = User.objects.get()
            # custom = UserProfile(user = t)
            # custom.user_id = t.id
            recipe.creatorID = request.user
            recipe.save()

        if formset2.is_valid():
            contents = recipeContent2.objects.create()
            contents.quantity = formset2.data["quantity"]
            i = formset2.data["ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset2.data["measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents.recipeID = r
            contents.save()

        if formset3.is_valid():
            contents2 = recipeContent2.objects.create()
            contents2.quantity = formset3.data["quantity"]
            i = formset3.data["ingredientID"]

            ingred = ingredient2.objects.get(pk=i)

            contents2.ingredientID = ingred
            m = formset3.data["measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents2.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents2.recipeID = r
            contents2.save()

        if formset4.is_valid():
            contents3 = recipeContent2.objects.create()
            contents3.quantity = formset4.data["quantity"]
            i = formset4.data["ingredientID"]

            ingred = ingredient2.objects.get(pk=i)
            contents3.ingredientID = ingred
            m = formset4.data["measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents3.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents3.recipeID = r
            contents3.save()

        d = {"user": request.user}
        return render_to_response('create.html', d)








