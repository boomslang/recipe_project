# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.contrib import messages
from django.forms.models import modelformset_factory
from main.models import UserForm, UserProfile, recipeForm, recipeClass1, recipeContent2, recipeContents_form, ingredient2, measurementUnit2, Like, Tag, UserTagRecipe
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
        userprofile1=UserProfile()
        user_createdRecipes = recipeClass1.objects.filter(creatorID=request.user.id) #active user_id ?
       # user_to_view2 = User.objects.get(username = user_name)
        user_likedRecipes = Like.objects.filter(user=request.user)
        d = {"user": request.user, "createdRecipes1": user_createdRecipes, "UserProfile1": userprofile1,
             "likedRecipes1": user_likedRecipes}
        d.update(csrf(request))
        return render_to_response('profile.html', d)


@login_required
def create_view(request):
    if request.method == 'GET':
        recipe_form1 = recipeForm()
        #ingredient_form1 = ingredient_form()
        #measurement_form1 = measurement_form()

        recipeContents_form1 = recipeContents_form(prefix="a")
        recipeContents_form2 = recipeContents_form(prefix="b")
        recipeContents_form3 = recipeContents_form(prefix="c")
        recipeContents_form4 = recipeContents_form(prefix="d")
        recipeContents_form5 = recipeContents_form(prefix="e")



        d = {"user": request.user, "recipeForm1": recipe_form1, "recipeContentForm1": recipeContents_form1,
             "recipeContentForm2": recipeContents_form2, "recipeContentForm3": recipeContents_form3, "recipeContentForm4": recipeContents_form4, "recipeContentForm5": recipeContents_form5}
        d.update(csrf(request))
        return render_to_response('create.html', d)
    else:
        formset1 = recipeForm(request.POST, request.FILES)
        formset2 = recipeContents_form(request.POST, request.FILES, prefix="a")
        formset3 = recipeContents_form(request.POST, request.FILES, prefix="b")
        formset4 = recipeContents_form(request.POST, request.FILES, prefix="c")
        formset5 = recipeContents_form(request.POST, request.FILES, prefix="d")
        formset6 = recipeContents_form(request.POST, request.FILES, prefix="e")

        if formset1.has_changed():
            recipe = recipeClass1.objects.create()
            recipe.recipeName = formset1.data["recipeName"]
            recipe.recipeDesc = formset1.data["recipeDesc"]
            # recipe.creationDateTime = formset.data["creationDateTime"]
            # t = {"user": request.user}
            #c = User.objects.get()
            # custom = UserProfile(user = t)
            # custom.user_id = t.id
            recipe.creatorID = request.user
            recipe.save()

        if formset2.has_changed():
            contents = recipeContent2.objects.create()
            contents.quantity = formset2.data["a-quantity"]
            i = formset2.data["a-ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset2.data["a-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents.recipeID = r
            contents.save()

        if formset3.has_changed():
            contents2 = recipeContent2.objects.create()
            contents2.quantity = formset3.data["b-quantity"]
            i = formset3.data["b-ingredientID"]

            ingred = ingredient2.objects.get(pk=i)

            contents2.ingredientID = ingred
            m = formset3.data["b-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents2.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents2.recipeID = r
            contents2.save()

        if formset4.has_changed():
            contents3 = recipeContent2.objects.create()
            contents3.quantity = formset4.data["c-quantity"]
            i = formset4.data["c-ingredientID"]

            ingred = ingredient2.objects.get(pk=i)
            contents3.ingredientID = ingred
            m = formset4.data["c-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents3.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents3.recipeID = r
            contents3.save()

        if formset5.has_changed():
            contents4 = recipeContent2.objects.create()
            contents2.quantity = formset5.data["d-quantity"]
            i = formset5.data["d-ingredientID"]

            ingred = ingredient2.objects.get(pk=i)

            contents4.ingredientID = ingred
            m = formset5.data["d-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents4.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents4.recipeID = r
            contents4.save()

        if formset6.has_changed():
            contents5 = recipeContent2.objects.create()
            contents5.quantity = formset4.data["e-quantity"]
            i = formset6.data["e-ingredientID"]

            ingred = ingredient2.objects.get(pk=i)
            contents5.ingredientID = ingred
            m = formset6.data["e-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents5.measurementUnitID = meas
            r = recipeClass1.objects.get(recipeName=recipe.recipeName)
            contents5.recipeID = r
            contents5.save()

        return mainPage_view(request)
       # d = {"user": request.user}
       # return render_to_response('profile.html', d)


@login_required()
def recipe_view(request, recipe_id = None):
    recipe = recipeClass1.objects.get(pk = recipe_id)

    creator_name = recipe.creatorID
    numberLikes= Like.objects.filter(recipe=recipe).count()
    recipe_contents =  recipeContent2.objects.filter(recipeID = recipe)

    content = []
    for recipe_content in recipe_contents:
        amount = str(recipe_content.quantity)
        if recipe_content.measurementUnitID:
            amount += " " + recipe_content.measurementUnitID.measurementUnitName
        content.append({'amount' : amount, 'ingredient' : recipe_content.ingredientID})

    liked = False
    try:
        Like.objects.get(user = request.user, recipe = recipe)
        liked = True
    except:
        pass

    d = {'user':request.user, 'recipe' : recipe, 'creator_name': creator_name, 'content':content, 'liked': liked,
         'numberLikes1': numberLikes}
    return render_to_response('recipe.html', d)



@login_required()
def user_view(request, user_name = None):
    user_to_view = User.objects.get(username = user_name)
    karma = UserProfile.objects.get(user = user_to_view).karma

    recipes = recipeClass1.objects.filter(creatorID = user_to_view)
    likedRecipes = Like.objects.filter(user = user_to_view)
    d = {'user':request.user, 'user_to_view':user_to_view,'karma' : karma, 'recipes': recipes,
         'likedRecipes1': likedRecipes}
    return render_to_response('user.html', d)

@login_required()
def ajax_like(request):
    if not request.is_ajax():
        raise Http404

    recipe_id = request.GET.get('recipe_id')
    recipe = recipeClass1.objects.get(pk = recipe_id)

    try:
        Like.objects.get(user = request.user, recipe = recipe).delete()
    except ObjectDoesNotExist:
        Like.objects.create(user = request.user, recipe = recipe)

    return HttpResponse({}, mimetype='application/json')