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
from django.forms.models import modelform_factory
from main.models import UserForm, UserProfile, recipeForm, recipeClass1, recipeContent2, recipeContents_form, ingredient2, measurementUnit2, Like, Mutate, ReplacedIngredients
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
    recipe_form1 = modelform_factory(recipeClass1, form=recipeForm)
    recipeContentsForm = modelform_factory(recipeContent2, form=recipeContents_form)

    if request.method == 'GET':


        recipeContents_form1 = recipeContentsForm(prefix="a")
        recipeContents_form2 = recipeContentsForm(prefix="b")
        recipeContents_form3 = recipeContentsForm(prefix="c")
        recipeContents_form4 = recipeContentsForm(prefix="d")
        recipeContents_form5 = recipeContentsForm(prefix="e")



        d = {"user": request.user, "recipeForm1": recipe_form1, "recipeContentForm1": recipeContents_form1,
             "recipeContentForm2": recipeContents_form2, "recipeContentForm3": recipeContents_form3, "recipeContentForm4": recipeContents_form4, "recipeContentForm5": recipeContents_form5}
        d.update(csrf(request))
        return render_to_response('create.html', d)
    else:

        formset1 = recipe_form1(request.POST, request.FILES)
        formset2 = recipeContentsForm(request.POST, request.FILES, prefix="a")
        formset3 = recipeContentsForm(request.POST, request.FILES, prefix="b")
        formset4 = recipeContentsForm(request.POST, request.FILES, prefix="c")
        formset5 = recipeContentsForm(request.POST, request.FILES, prefix="d")
        formset6 = recipeContentsForm(request.POST, request.FILES, prefix="e")

        if formset1.has_changed() and (formset2.has_changed() or formset3.has_changed() or formset4.has_changed() or formset5.has_changed() or formset6.has_changed()):
            recipe = recipeClass1.objects.create()
            recipe.recipeName = formset1.data["recipeName"]
            recipe.recipeDesc = formset1.data["recipeDesc"]
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
                r = recipeClass1.objects.get(id=recipe.id)
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
                r = recipeClass1.objects.get(id=recipe.id)
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
                r = recipeClass1.objects.get(id=recipe.id)
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
                r = recipeClass1.objects.get(id=recipe.id)
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
                r = recipeClass1.objects.get(id=recipe.id)
                contents5.recipeID = r
                contents5.save()


        return HttpResponseRedirect('/u/%s' % request.user)

@login_required()
def recipe_view(request, recipe_id = None):
    recipe = recipeClass1.objects.get(pk = recipe_id)

    creator_name = recipe.creatorID

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

    d = {'user':request.user, 'recipe' : recipe, 'creator_name': creator_name, 'content':content, 'liked': liked }
    return render_to_response('recipe.html', d)

@login_required()
def user_view(request, user_name = None):
    user_to_view = User.objects.get(username = user_name)
    karma = UserProfile.objects.get(user = user_to_view).karma

    recipes = recipeClass1.objects.filter(creatorID = user_to_view)
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
    recipe = recipeClass1.objects.get(pk = recipe_id)

    try:
        Like.objects.get(user = request.user, recipe = recipe).delete()
    except ObjectDoesNotExist:
        Like.objects.create(user = request.user, recipe = recipe)

    return HttpResponse({}, mimetype='application/json')

@login_required()
def mutate_view(request, recipe_id = None):
    recipe = recipeClass1.objects.get(pk = recipe_id)
    recipe_contents =  recipeContent2.objects.filter(recipeID = recipe)


    recipe_form1 = recipeForm(instance=recipe)

    recipeContents_form1 = recipeContents_form(prefix="a")
    recipeContents_form2 = recipeContents_form(prefix="b")
    recipeContents_form3 = recipeContents_form(prefix="c")
    recipeContents_form4 = recipeContents_form(prefix="d")
    recipeContents_form5 = recipeContents_form(prefix="e")
    if len(recipe_contents) > 0:
        recipeContents_form1 = recipeContents_form(instance=recipe_contents[0], prefix="a")
    if len(recipe_contents) > 1:
        recipeContents_form2 = recipeContents_form(instance=recipe_contents[1], prefix="b")
    if len(recipe_contents) > 2:
        recipeContents_form3 = recipeContents_form(instance=recipe_contents[2], prefix="c")
    if len(recipe_contents) > 3:
        recipeContents_form4 = recipeContents_form(instance=recipe_contents[3], prefix="d")
    if len(recipe_contents) > 4:
        recipeContents_form5 = recipeContents_form(instance=recipe_contents[4], prefix="e")


    if request.method == 'GET':

        d = {"user": request.user, "recipeForm1": recipe_form1, "recipeContentForm1": recipeContents_form1,
             "recipeContentForm2": recipeContents_form2, "recipeContentForm3": recipeContents_form3, "recipeContentForm4": recipeContents_form4, "recipeContentForm5": recipeContents_form5}
        d.update(csrf(request))
        return render_to_response('mutate.html', d)

    else:

        formset1 = recipeForm(request.POST, instance=recipe)
        formset2 = recipeContents_form(request.POST, prefix="a")
        formset3 = recipeContents_form(request.POST, prefix="b")
        formset4 = recipeContents_form(request.POST, prefix="c")
        formset5 = recipeContents_form(request.POST, prefix="d")
        formset6 = recipeContents_form(request.POST, prefix="e")
        if len(recipe_contents) > 0:
            formset2 = recipeContents_form(request.POST, instance=recipe_contents[0], prefix="a")
            if recipe_contents[0].ingredientID.id != formset2.data["a-ingredientID"]:
                originalIng = ingredient2.objects.get(id=recipe_contents[0].ingredientID.id)
                replacedIng = ingredient2.objects.get(id=formset2.data["a-ingredientID"])
                try:
                    new_replacedIngredient = ReplacedIngredients.objects.get(original_ingredient__in=[originalIng, replacedIng], replaced_ingredient__in=[originalIng,replacedIng])
                    new_replacedIngredient.count += 1
                    new_replacedIngredient.save()
                except ObjectDoesNotExist:
                    new_replacedIngredient = ReplacedIngredients.objects.create(original_ingredient=originalIng, replaced_ingredient=replacedIng, count=1)
        if len(recipe_contents) > 1:
            formset3 = recipeContents_form(request.POST, instance=recipe_contents[1], prefix="b")
        if len(recipe_contents) > 2:
            formset4 = recipeContents_form(request.POST, instance=recipe_contents[2], prefix="c")
        if len(recipe_contents) > 3:
            formset5 = recipeContents_form(request.POST, instance=recipe_contents[3], prefix="d")
        if len(recipe_contents) > 4:
            formset6 = recipeContents_form(request.POST, instance=recipe_contents[4], prefix="e")

        if formset1.is_valid() and formset1.data["recipeName"] != "":
            new_recipe = recipeClass1.objects.create()
            new_recipe.recipeName = formset1.data["recipeName"]
            new_recipe.recipeDesc = formset1.data["recipeDesc"]
            new_recipe.creatorID = request.user
            new_recipe.save()

        if formset2.has_changed():

            contents = recipeContent2.objects.create()
            contents.quantity = formset2.data["a-quantity"]
            i = formset2.data["a-ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset2.data["a-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(id=new_recipe.id)
            contents.recipeID = r
            contents.save()
        if formset3.has_changed():

            contents = recipeContent2.objects.create()
            contents.quantity = formset3.data["b-quantity"]
            i = formset3.data["b-ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset3.data["b-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(id=new_recipe.id)
            contents.recipeID = r
            contents.save()
        if formset4.has_changed():

            contents = recipeContent2.objects.create()
            contents.quantity = formset4.data["c-quantity"]
            i = formset4.data["c-ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset4.data["c-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(id=new_recipe.id)
            contents.recipeID = r
            contents.save()
        if formset5.has_changed():

            contents = recipeContent2.objects.create()
            contents.quantity = formset5.data["d-quantity"]
            i = formset5.data["d-ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset5.data["d-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(id=new_recipe.id)
            contents.recipeID = r
            contents.save()
        if formset6.has_changed():

            contents = recipeContent2.objects.create()
            contents.quantity = formset6.data["e-quantity"]
            i = formset6.data["e-ingredientID"]
            ingred = ingredient2.objects.get(pk=i)
            contents.ingredientID = ingred
            m = formset6.data["e-measurementUnitID"]
            meas = measurementUnit2.objects.get(pk=m)
            contents.measurementUnitID = meas
            r = recipeClass1.objects.get(id=new_recipe.id)
            contents.recipeID = r
            contents.save()


        new_mutated_object = Mutate.objects.create(user=request.user, sourceRecipeID=recipe, mutatedRecipeID=r)



        return HttpResponseRedirect('/u/%s' % request.user)
