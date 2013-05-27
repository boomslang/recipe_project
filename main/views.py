# Create your views here.

from itertools import chain
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.contrib import messages
from django.forms.models import modelformset_factory
from django.forms.models import modelform_factory
from main.models import UserForm, UserProfile, RecipeForm, Recipe, RecipeContent, RecipeContentForm, Ingredient, MeasurementUnit, Like, Mutate, ReplacedIngredients, Tag,TagForm, UserTagRecipe, SearchForm
from recipe_project.settings import STATIC_URL

from datetime import datetime

def mainPage_view(request):
    add_ingredients()
    add_measurement_units()

    page_size = 5
    recipe_list = []
    page = request.GET.get('page')

    if request.method == 'POST':
        formset = SearchForm(request.POST, request.FILES)
        if formset.is_valid():
            query = formset.data['query']
            # recipe_list = Recipe.objects.filter(recipeName__icontains=query).order_by('-creationDateTime')
            recipe_list = search_recipe(query)
            print 'test'
            request.session['query'] = query

        else:
            recipe_list = Recipe.objects.all().order_by('-creationDateTime')
    elif page:
        query = request.session.get('query', False)
        if query:
            recipe_list = search_recipe(query)
        else:
            recipe_list = Recipe.objects.all().order_by('-creationDateTime')
    else:
        recipe_list = Recipe.objects.all().order_by('-creationDateTime')
        try:
            del request.session['query']
        except KeyError:
            pass

    paginator = Paginator(recipe_list, page_size)

    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        recipes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        recipes = paginator.page(paginator.num_pages)

    search_form = SearchForm(auto_id=False)
    d = {"formset": search_form, "recipes": recipes, "user": request.user}
    d.update(csrf(request))
    return render_to_response('main_page.html', d)

def search_recipe(query):
    recipe_list= list(Recipe.objects.filter(Q(recipeName__icontains=query) | Q(recipeDesc__icontains=query) | Q(creator__username=query)))
    UTRs = UserTagRecipe.objects.filter(tag__description=query)
    recipe_list2 = [UTR.recipe for UTR in UTRs]

    result_list = sorted(
        chain(recipe_list, recipe_list2),
        key=lambda instance: instance.creationDateTime)
    # recipe_list = list(set(list(recipe_list)) | set(recipe_list2))

    return result_list

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
       #  userprofile1=UserProfile()
       #  user_createdRecipes = Recipe.objects.filter(creator=request.user.id) #active user_id ?
       # # user_to_view2 = User.objects.get(username = user_name)
       #  user_likedRecipes = Like.objects.filter(user=request.user)
       #  d = {"user": request.user, "createdRecipes1": user_createdRecipes, "UserProfile1": userprofile1,
       #       "likedRecipes1": user_likedRecipes}
       #  d.update(csrf(request))
       #  return render_to_response('profile.html', d)
        return HttpResponseRedirect('/u/%s' % request.user)


@login_required
def create_view(request):
    max_ingredients = 10
    if request.method == 'GET':

        recipe_form = RecipeForm(instance=Recipe())
        rc_forms = [RecipeContentForm(prefix=str(x), instance=RecipeContent()) for x in range(0,max_ingredients)]

        d = {"user": request.user, "recipe_form": recipe_form, "rc_forms": rc_forms}
        d.update(csrf(request))
        return render_to_response('create.html', d)
    else:
        recipe_form = RecipeForm(request.POST, instance=Recipe())
        rc_forms = [RecipeContentForm(request.POST, prefix=str(x), instance=RecipeContent()) for x in range(0,max_ingredients)]
        for f in rc_forms:
            print f.has_changed()

        if recipe_form.is_valid() and any([rc_form.is_valid() for rc_form in rc_forms]):
            recipe = Recipe.objects.create()
            recipe.recipeName = recipe_form.data["recipeName"]
            recipe.recipeDesc = recipe_form.data["recipeDesc"]
            recipe.creator = request.user
            recipe.creationDateTime = datetime.now()
            recipe.save()

            for ind,rc_form in enumerate(rc_forms):
                if rc_form.is_valid():
                    recipe_content = rc_form.save(commit=False)
                    recipe_content.recipe = recipe
                    recipe_content.save()


            return HttpResponseRedirect('/r/%s' % recipe.id)
        else:
            d = {"user": request.user, "recipe_form": recipe_form, "rc_forms": rc_forms, "error":True}
            d.update(csrf(request))
            return render_to_response('create.html', d)

@login_required()
def recipe_view(request, recipe_id = None):
    recipe = Recipe.objects.get(pk = recipe_id)

    creator_name = recipe.creator
    # numberLikes= Like.objects.filter(recipe=recipe).count()
    numberLikes= recipe.num_likes

    recipe_contents = RecipeContent.objects.filter(recipe = recipe)
    recipeTags= UserTagRecipe.objects.filter(recipe=recipe)

    content = []
    for recipe_content in recipe_contents:
        amount = str(recipe_content.quantity)
        if recipe_content.measurementUnit:
            amount += " " + recipe_content.measurementUnit.measurementUnitName
        content.append({'amount' : amount, 'ingredient' : recipe_content.ingredient})

    liked = False
    try:
        Like.objects.get(user = request.user, recipe = recipe)
        liked = True
    except:
        pass

    d = {'user':request.user, 'recipe' : recipe, 'creator_name': creator_name, 'content':content, 'liked': liked,
         'numberLikes1': numberLikes, 'recipeTags1': recipeTags}
    return render_to_response('recipe.html', d)

@login_required()
def tag_view(request, recipe_id = None):

    recipe = Recipe.objects.get(pk = recipe_id)

    if request.method=='GET':
        TagForm1= TagForm()
        d= {'user': request.user, 'tagForm1': TagForm1}
        d.update(csrf(request))
        return render_to_response('tag.html', d)
    else:
        TagFormset=TagForm(request.POST, request.FILES)

        if TagFormset.has_changed():
            tags = Tag.objects.create(description=TagFormset.data['description'])
            tags.save()

            user_tags=UserTagRecipe.objects.create(user=request.user, recipe=recipe, tag=tags)
            user_tags.save()

        return HttpResponseRedirect('/r/%s' % recipe.id)

@login_required()
def user_view(request, user_name = None):
    user_to_view = User.objects.get(username = user_name)
    karma = UserProfile.objects.get(user = user_to_view).karma

    recipes = Recipe.objects.filter(creator = user_to_view)
    likedRecipes = Like.objects.filter(user = user_to_view)
    mutatedRecipes = Mutate.objects.filter(user=user_to_view)
    d = {'user':request.user, 'user_to_view':user_to_view,'karma' : karma, 'recipes': recipes,
         'likedRecipes1': likedRecipes, 'mutatedRecipes': mutatedRecipes}
    return render_to_response('user.html', d)


@login_required()
def ajax_like(request):
    if not request.is_ajax():
        raise Http404

    recipe_id = request.GET.get('recipe_id')
    recipe = Recipe.objects.get(pk = recipe_id)
    author = UserProfile.objects.get(pk = recipe.creator)


    try:
        like = Like.objects.get(user = request.user, recipe = recipe).delete()
        author.karma -= 1
        recipe.num_likes -= 1

    except ObjectDoesNotExist:
        Like.objects.create(user = request.user, recipe = recipe)
        author.karma += 1
        recipe.num_likes += 1

    author.save()
    recipe.save()
    return HttpResponse({}, mimetype='application/json')

@login_required()
def mutate_view(request, recipe_id = None):
    max_ingredients = 10
    original_recipe = Recipe.objects.get(pk = recipe_id)
    recipe_contents = RecipeContent.objects.filter(recipe = original_recipe)

    if request.method == 'GET':


        recipe_form = RecipeForm(instance=original_recipe)
        rc_forms = [RecipeContentForm(prefix=str(ind), instance=rc) for ind,rc in enumerate(recipe_contents)]
        while len(rc_forms) != max_ingredients:
            rc_forms.append(RecipeContentForm(prefix=str(len(rc_forms)), instance=RecipeContent()))


        d = {"user": request.user, "recipe_form": recipe_form, "rc_forms": rc_forms}
        d.update(csrf(request))
        return render_to_response('mutate.html', d)

    else:
        recipe_form = RecipeForm(request.POST, instance=Recipe())
        rc_forms = [RecipeContentForm(request.POST, prefix=str(x), instance=RecipeContent()) for x in range(0,max_ingredients)]
        for f in rc_forms:
            print f.has_changed()

        if recipe_form.is_valid() and any([rc_form.is_valid() for rc_form in rc_forms]):
            recipe = Recipe.objects.create()
            recipe.recipeName = recipe_form.data["recipeName"]
            recipe.recipeDesc = recipe_form.data["recipeDesc"]
            recipe.creator = request.user
            recipe.creationDateTime = datetime.now()
            recipe.save()

            Mutate.objects.create(user=request.user, source_recipe=original_recipe, mutated_recipe=recipe)

            for ind,rc_form in enumerate(rc_forms):
                if rc_form.is_valid():
                    recipe_content = rc_form.save(commit=False)
                    recipe_content.recipe = recipe
                    recipe_content.save()
                    new_ingredient_id = rc_form.data[str(ind) + '-ingredient']
                    if len(recipe_contents) > ind and str(recipe_contents[ind].ingredient.id) != new_ingredient_id:
                        originalIng = Ingredient.objects.get(pk = recipe_contents[ind].ingredient.id)
                        replacedIng = Ingredient.objects.get(pk = new_ingredient_id)
                        # new_replacedIngredient = ReplacedIngredients.objects.get_or_create(original_ingredient__in=[originalIng, replacedIng], replaced_ingredient__in=[originalIng,replacedIng])
                        new_replacedIngredient,succeed = ReplacedIngredients.objects.get_or_create(original_ingredient=originalIng, replaced_ingredient=replacedIng)
                        new_replacedIngredient.count += 1
                        new_replacedIngredient.save()


            return HttpResponseRedirect('/r/%s' % recipe.id)
        else:
            d = {"user": request.user, "recipe_form": recipe_form, "rc_forms": rc_forms, "error":True}
            d.update(csrf(request))
            return render_to_response('mutate.html', d)


def add_ingredients():
    items = ["orange","olive oil","spinach","onion","sugar","salt","water","egg","rice","beef","tomato"]
    for item in items:
        Ingredient.objects.get_or_create(ingredientName = item)
def add_measurement_units():
    items = ["lt","ml","piece","unit","pound","kg","gram","tablespoon","teaspoon","cup"]
    for item in items:
        MeasurementUnit.objects.get_or_create(measurementUnitName = item)
