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
from main.models import UserForm, UserProfile, RecipeForm, Recipe, RecipeContent, RecipeContentForm, Ingredient, MeasurementUnit, Like, Mutate, ReplacedIngredients, Tag,TagForm, UserTagRecipe, SearchForm, RecipeAndRecipeContent, Replacement, MutateAndReplacement
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

    return result_list[::-1]

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
                    rc, found = RecipeContent.objects.get_or_create(ingredient=recipe_content.ingredient,measurementUnit=recipe_content.measurementUnit,quantity=recipe_content.quantity)
                    RecipeAndRecipeContent.objects.create(recipe=recipe, recipe_content=rc)

            return HttpResponseRedirect('/r/%s' % recipe.id)
        else:
            d = {"user": request.user, "recipe_form": recipe_form, "rc_forms": rc_forms, "error":True}
            d.update(csrf(request))
            return render_to_response('create.html', d)

@login_required()
def recipe_view(request, recipe_id = None):
    """

    :param request:
    :param recipe_id:
    """
    recipe = Recipe.objects.get(pk = recipe_id)

    creator_name = recipe.creator
    # numberLikes= Like.objects.filter(recipe=recipe).count()
    numberLikes= recipe.num_likes

    recipe_contents = RecipeAndRecipeContent.objects.filter(recipe = recipe)

    ids = RecipeAndRecipeContent.objects.values_list('recipe_content', flat=True).filter(recipe=recipe)
    recipe_contents = RecipeContent.objects.filter(pk__in=set(ids))

    recipeTags= UserTagRecipe.objects.filter(recipe=recipe)

    content = []
    for recipe_content in recipe_contents:
        amount = str(recipe_content.quantity)

        if amount[-2:]=='.0':
            amount = amount[:-2]

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
            try:
                tags = Tag.objects.get(description=TagFormset.data['description'])

            except ObjectDoesNotExist:
                tags = Tag.objects.create(description=TagFormset.data['description'])
                tags.save()

            try:
                user_tags=UserTagRecipe.objects.get(recipe=recipe, tag=tags)

            except ObjectDoesNotExist:
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
    ids = RecipeAndRecipeContent.objects.values_list('recipe_content', flat=True).filter(recipe=original_recipe)
    recipe_contents = RecipeContent.objects.filter(pk__in=set(ids))

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

            mutation = Mutate.objects.create(user=request.user, source_recipe=original_recipe, mutated_recipe=recipe)

            for ind,rc_form in enumerate(rc_forms):
                if rc_form.is_valid():
                    recipe_content = rc_form.save(commit=False)
                    rc, found = RecipeContent.objects.get_or_create(ingredient=recipe_content.ingredient,measurementUnit=recipe_content.measurementUnit,quantity=recipe_content.quantity)
                    RecipeAndRecipeContent.objects.create(recipe=recipe, recipe_content=rc)

                    if len(recipe_contents) > ind:
                        new_i = recipe_content.ingredient
                        new_m = recipe_content.measurementUnit
                        new_q = recipe_content.quantity
                        original_rc = recipe_contents[ind]

                        old_i = original_rc.ingredient
                        old_m = original_rc.measurementUnit
                        old_q = original_rc.quantity

                        if old_i != new_i or old_m != new_m or old_q != new_q:
                            replacement = Replacement.objects.create(original_rc=original_rc, new_rc=rc)
                            MutateAndReplacement.objects.create(mutation=mutation,replacement=replacement)

                        if old_i != new_i:
                            # new_replacedIngredient = ReplacedIngredients.objects.get_or_create(original_ingredient__in=[originalIng, replacedIng], replaced_ingredient__in=[originalIng,replacedIng])
                            new_replacedIngredient,succeed = ReplacedIngredients.objects.get_or_create(original_ingredient=old_i, replaced_ingredient=new_i)
                            new_replacedIngredient.count += 1
                            new_replacedIngredient.save()

            return HttpResponseRedirect('/r/%s' % recipe.id)
        else:
            d = {"user": request.user, "recipe_form": recipe_form, "rc_forms": rc_forms, "error":True}
            d.update(csrf(request))
            return render_to_response('mutate.html', d)


def add_ingredients():
    items = ["Chili pepper",
             "Cubeb","Turmeric","Chives","Tarragon","Buddha's hand","Chayote","Blueberry","Fennel","Cardoon","Onion",
             "Veal","Sirloin steak","Bacon","Tomato","Bean","Pasta","Butternut squash","Fruit","Cream","Rice","Mustard",
             "Ketchup","Worcestershire sauce","Sambal","Lentil","Potato","Lamb and mutton","Pork","Sourdough","Yeast",
             "Baking powder","Corn tortilla","Meat","Flour","Milk","Egg","Butter","Ginger","Pumpkin","Shortening",
             "Cinnamon","Nutmeg","Chocolate","Beef mince","Seaweed","Apple","Kimchi","Horseradish","Soy sauce",
             "Reshteh","Spatzle","Tagliatelle","Lamian","Mee pok","Somen","Udon","Rice vermicelli","Shahe fen",
             "Cellophane noodles","Soba","Campanelle","Cavatelli","Cencioni","Conchiglie","Croxetti","Farfalle",
             "Foglie d'ulivo","Fusilli","Lanterne","Orecchiette","Radiatori","Rotelle","Rotini","Strozzapreti",
             "Bucatini","Cannelloni","Cavatappi","Macaroni","Mostaccioli","Penne","Rigatoni","Ziti","Spaghetti",
             "Spaghettini","Vermicelli","Capellini","Pici","Fettuccine","Lasagnette","Linguine","Mafaldine",
             "Pappardelle","Pizzoccheri","Trenette","Alphabet pasta","Anellini","Fregula","Orzo","Agnolotti",
             "Manti","Tortellini","Ham","Stottie cake","Chapati","Kulcha","Brioche","Biscuit","Damper","Meringue",
             "Mincemeat","Peach","Raspberry","Corn syrup","Pecan","Coconut milk","Tuna","Green bean","Olive","Sugar",
             "Rhubarb","Bell pepper","Celery","Chorizo","Crouton","Romaine lettuce","Anchovy","Parmigiano-Reggiano",
             "Mayonnaise","Walnut","Olive oil","Cucumber","Oregano","Spam","Chicken meat","Back bacon","Almond",
             "Sodium bicarbonate","Peanut","Cashew","Galangal","Annatto","Coriander","Rosemary","Star Anise",
             "Common sage","Cardamom","Chamaemelum nobile","Saffron","Cumin","Tamarind","Lemongrass","Caraway",
             "Clove","Fenugreek","Paprika","Sumac","Sichuan pepper","Mustard seed","Allspice","Basil","Marjoram",
             "Mint","Thyme","Dill","Parsley","Bay Laurel","Scarlet beebalm","Salad burnet","Hyssopus","Lemon Beebrush",
             "Lovage","Satureja","Perilla frutescens","Cicely","Garlic chives","Carnaroli rice","Arborio rice","Roe",
             "Yam","Sauerkraut","Shallot","Pea","Spinach","Summer squash","Sweet potato","Tomatillo","Turnip greens",
             "Watercress","Winter squash","Chinese cabbage","Collard greens","Scallion","Kale","Leek","Mustard Greens",
             "Alfalfa sprouts","Salad Rocket","Bean sprouts","Beet Greens","Broccoli","Broccoflower","Brussels sprout",
             "Cabbage","Cauliflower","Chard","Beet","Artichoke","Artichoke Hearts","Asparagus","Avocado","Chickpea",
             "Chile peppers","Eggplant","Endive","Kidney beans","Kohlrabi","Navy Beans","Split pea","Turnip",
             "Radicchio","Rutabaga","Zucchini","Bamboo shoot","Maize","Phaseolus lunatus","Edible mushroom",
             "Lettuce","Iceburg Lettuce","Red Leaf Lettuce","Water Chestnut","Watermelon","Blackberry","Cantaloupe",
             "Cherry","Cranberry","Date palm","Dried fruit","Grapefruit","Grape","Guava","Kiwifruit","Lemon","Lime",
             "Mango","Nectarine","Orange","Papaya","Pyrus pyrifolia","Persimmon","Pineapple","Plum","Fragaria",
             "Tangerine","Ugli fruit","Banana","Cheese","Jell-O","Juniper","Meat analogue","Wheat","Black-eyed pea",
             "Chesapeake blue crab","Horse mackerel","Yoghurt","Curd","Vegetable","Table salt","Vinegar",
             "Tabasco pepper","Jalapeno","Kingston Black Apple","Orris root","Juniper berry","Soybean",
             "Truffle","Horsehair crab","Spiny lobster","Caridean Shrimp","Suckling pig","Crab","Mantis shrimp",
             "Marlin","Abalone","Lobster","Stingray","Sole","Sardine","Beef","Pork belly","Foie gras","Century egg",
             "Umeboshi","Squid","Snapper","Melon","King crab","Sea urchin","Mishima beef","Oxtail","Tilefish",
             "Conger","Cod","Venison","Curry powder","Common snapping turtle","Garlic","Beef tongue","Tofu","Oyster",
             "Soft-shell crab","Salmon","Chestnut","Matsutake","Carrot","Octopus","Winter melon","Sturgeon",
             "Stock Dove","Daikon","Eel","Bonito","Taro","Red seabream","Pear","Carp","Ayu","Liver",
             "Sea cucumber","Red snapper","Hamo","Scallop","Anglerfish","Sauries","Shiitake","Pufferfish","Honey",
             "Flounder","Crayfish","Anago","Cuttlefish","Scorpionfish","Wine","Wakame","Dried Abalone",
             "Managatsuo Tuna","Taisho  Shrimp","Black Tiger Shrimp","Salmon Roe","Cod Roe","Jumbo Mushroom",
             "Supreme  Squid","Pen Shell  Clams","Bird's Nest","Scampi Shrimp","Sea Bass","Jinhua Pork",
             "Matsuba Crab","Fatty Tuna","Red fish","Dried Scallop","Salted Salmon","Botan Shrimp",
             "Short Neck  Clams","Iwa Oyster","Giant Lobster","Porcini Mushroom","Hamaguri Clams",
             "Shanghai Crab","Giant Eel","Asyura Oyster","Takaashi Crab","Juvenile Salmon","Black Pig",
             "Spanish  Mackerel","Beef Cheek","Cod Soft Roe","Kinoko Mushroom","Maitake Mushroom","Ara (fish)",
             "Pomegranate","Buttermilk","Ground meat","Boiled egg","Water","Schmaltz","Lemon juice","Tahini",
             "Groat","Blood","Lard","Duxelles","Beef tenderloin","Pancetta","Pecorino Romano","Guanciale",
             "Habanero chili","urad dal","Oaxaca cheese","Pasilla","Nopal","Epazote","Corn smut","Masa","Plantain",
             "Pumpkin seed","Agave azul","Chipotle","Serrano pepper","Pomelo","Maple syrup","Amaranth",
             "Rice noodles","Rice paper","Fish sauce","Mung bean","Glutinous rice","Whipped cream","Choux pastry",
             "Semolina","Short ribs","Herring","Bagoong terong","Bagoong monamon","Purple yam","Creme de Marrons",
             "Ghee","Caerphilly cheese","Bread crumbs","Candied fruit","Raisin","cream of tartar","Scotch whisky",
             "Oatmeal","Haddock","Barley","Shrimp paste","Water spinach","Coconut","Pork chop","Pork loin",
             "Cabbage in Connecticut","Meyer lemon","Blood orange","Bitter orange","Capsicum","Garlic scape",
             "Fiddlehead fern","Apricot","Passion fruit","Opuntia","Purple mangosteen","Common Fig","Sweet corn",
             "Bitter melon","Rapini","Ironweed","Flatweed","Celtuce","Malabar spinach","Chicory","Malva","Daisy",
             "Corn salad","Garden cress","Taraxacum","Lamb's Quarters","Fluted Pumpkin","Golden samphire",
             "Chenopodium bonus-henricus","Carpobrotus edulis","Acmella oleracea","Kai-lan","Komatsuna","Adansonia",
             "Waterleaf","Land Cress","Houttuynia","Corchorus","Mizuna","Sinapis","Tetragonia","Saltbush",
             "Phytolacca americana","Crithmum","Sea beet","Crambe maritima","Crassocephalum","Celosia","Sorrel",
             "Common Purslane","Tatsoi","Rapeseed","Breadfruit","Acorn squash","Ananas","Armenian cucumber","Caigua",
             "Peruvian groundcherry","Cayenne pepper","Luffa","Figleaf Gourd","Trichosanthes dioica","Coccinia grandis","Pattypan squash","Snake gourd","Squash","Tinda","West Indian gherkin","Potato bean","Azuki bean","Moringa","Hyacinth Bean","Broad bean","common bean","Guar","Horse gram","White pea","Moth bean","Okra","Pigeon pea","Ricebean","Runner bean","Lupinus mutabilis","Tepary bean","black gram","Velvet bean","Winged bean","Vigna unguiculata subsp. sesquipedalis","Asparagus","Celeriac","Elephant garlic","Kurrat","Sacred Lotus","Pyrenees star of Bethlehem","Welsh onion","ramp","Pachyrhizus","Arracacha","Black Cumin","Broadleaf Arrowhead","Camassia","Canna","Cassava","Stachys affinis","Lathyrus tuberosus","Elephant Foot Yam","Ensete","Greater Burdock","Jerusalem artichoke","Parsnip","Pignut","Plectranthus","Prairie Turnip","Radish","Tragopogon porrifolius","Black Salsify","Skirret","Ti plant","Yellow Nutgrass","Ulluco","Wasabi","Aonori","Callophyllis variegata","Dabberlocks","Dulse","Hijiki","Kombu","Cladosiphon okamuranus","Laver","Nori","Gim","Ogonori","Caulerpa","Sea lettuce","Chokeberry","Loquat","Mespilus","Quince","Rose hip","Rowan","Sorbus","Shadbush","Shipova","Chokecherry","Greengage","Pluot","Aprium","Peacotum","Dewberry","Boysenberry","Olallieberry","Tayberry","Cloudberry","Loganberry","Salmonberry","thimbleberry","Wine Raspberry","Bearberry","Bilberry","Crowberry","Huckleberry","Lingonberry","Strawberry tree","Strawberry","Berberis","Currant","Elderberry","Gooseberry","Celtis","Honeysuckle","Morus","Red Mulberry","White mulberry","Podophyllum","Viburnum lentago","Oregon Grape","Hippophae","Coccoloba uvifera","Goji","Luo Han Guo","Maclura tricuspidata","Durian","Elaeagnus multiflora","Hardy kiwi","Mock strawberry","Lansium domesticum","Choerospondias axillaris","Longan","Lychee","Borassus flabellifer","Rambutan","Sageretia theezans","Vitaceae","Podophyllum peltatum","American Persimmon","beach plum","Black Cherry","Shepherdia","Chrysobalanus icaco","Purple Passionflower","Asimina","Coccoloba diversifolia","Salal Chad","Saskatoon","Serenoa","Heteromeles","Atherton Raspberry","Black Apple","Melastoma affine","Eupomatia laurina","Burdekin Plum","Cedar Bay Cherry","Cluster Fig Tree","Billardiera scandens","Carissa lanceolata","Davidsonia","Desert fig","Desert Lime","Marsdenia australis","Emu Apple","Syzygium fibrosum","Finger Lime","Podocarpus elatus","Buchanania arborescens","Citrus gracilis","Australian desert raisin","Terminalia ferdinandiana","Carpobrotus rossii","Red bush apple","Lemon aspen","Austromyrtus dulcis","Tasmannia","Kunzea pomifera","Exocarpos cupressiformis","Wiry ground-berry","Native Gooseberry","Carpobrotus glaucescens","Native raspberry","Billardiera longiflora","Quandong","Riberry","West Indian Raspberry","Archirhodomyrtus beckleri","Sandpaper Fig","Diploglottis campbellii","Gaultheria hispida","Billardiera cymosa","Mimusops elengi","Acronychia oblongifolia","Capparis mitchellii","Manilkara kauki","Yellow Plum","Melodorum leichhardtii","Horned Melon","Galia","Muskmelon","Honeydew","Cornus mas","Fig","Jujube","Sycamore Fig","Citron","Clementine","Orangelo","Tangelo","Rangpur","Kumquat","Key lime","Persian lime","Kaffir lime","Mandarin orange","Sweet Lemon","Carob Tree","Feijoa","Annona glabra","Strawberry Guava","Tamarillo","Ugni","Myrica rubra","Pouteria caimito","Acerola","Ackee","African cherry orange","Amazon Grape","Eugenia stipitata","Babaco","Bael","Granadilla","Areca nut","Averrhoa bilimbi","Black Sapote","Calabash","Brazil nut","Burmese grape","Crescentia cujete","Myrciaria dubia","Pouteria campechiana","Carambola","Cempedak","Ceylon Gooseberry","Spanish Lime","Cherimoya","Star Apple","Coffee","Custard-apple","Damson","Pitaya","Giant granadilla","Golden Apple","Guarana","Guavaberry","Spondias","Genipa americana","Terminalia catappa","Barbary fig","Indian Jujube","Jabuticaba","Jackfruit","Jambul","Spondias purpurea","Leucaena","Pouteria lucuma","Diospyros blancoi","Macadamia","Mamey sapote","Madras Thorn","Marang","Melinjo","Pepino","Monstera deliciosa","Morinda","Annona","Mundu","Nanche","Naranjilla","Azadirachta indica","Elaeis","Peach Palm","Peanut Butter Fruit","Pequi","Pili nut","Ice-cream-bean","Syzygium malaccense","Pulasan","Salak","Manilkara zapota","Ilama","Soursop","Sugar-apple","Surinam Cherry","Sweet granadilla","Syzygium jambos","Vanilla","Syzygium samarangense","White sapote","Trachyspermum ammi","Alkanna tinctoria","Greater Galangal","Angelica","Anise","Ringwood","Apple Mint","Mugwort","Asafoetida","Bay leaf","Calendula","Jateorhiza calumba","Cananga odorata","Candlenut","Caper","Cinnamomum cassia","Casuarina","Nepeta","Centaurium","Chervil","Stitchwort","Cinchona","Backhousia myrtifolia","Salvia sclarea","Galium aparine","Clover","Comfrey","Common rue","Gonolobus condurango","Goldthread","Tanacetum balsamita","Elymus repens","Cow Parsley","Viburnum opulus","Mexican mint","Gnaphalium","Culantro","Curry tree","Damiana","Demulcent","Harpagophytum","Dorrigo Pepper","Purple Coneflower","Leontopodium alpinum","Elecampane","Siberian Ginseng","Emmenagogue","Ephedra","Eucalyptus","Euphrasia","Feverfew","Scrophularia","Fingerroot","Fumaria","Maidenhair Tree","Ginseng","Centella asiatica","Grains of Paradise","Grains of Selim","Grape seed extract","Green tea","Glechoma hederacea","Guaco","Lycopus europaeus","Hawthorn","Hibiscus","Holly","Hops","Humulus lupulus","Horehound","Equisetum","Jalap","Jasmine","Jiaogulan","John the Conqueror","Knotweed","Garcinia indica","Labrador tea","Lavender","Ledum","Lemon balm","Lemon basil","Eucalyptus staigeriana","Lemon Beebalm","Lemon myrtle","Liquorice","Limnophila aromatica","Lingzhi mushroom","Flax","Long pepper","Mahlab","Malabathrum","Marrubium vulgare","Marsh Labrador Tea","Pistacia lentiscus","Meadowsweet","Piper auritum","Milk thistle","Leonurus cardiaca","Large-flowered Skullcap","Mullein","Mustard plant","Pineapple Verbena","Nettle","Fennel Flower","Morinda citrifolia","Evening Primrose","Eucalyptus olida","Osmorhiza","Pandanus","Passion Flower","Patchouli","Pennyroyal","Black pepper","Peppermint","Eucalyptus dives","Perilla","Panch phoron","Poppy","Primula","Psyllium","Quassia","Ramsons","Ras el hanout","Ononis","Golden Root","Rooibos","Rue","Safflower","Saigon Cinnamon","Sage","Sassafras","Schisandra","Scarlet Skullcap","Senna","Sicklepod","Sesame","Sheep's sorrel","Sialagogue","Inonotus obliquus","Prunus spinosa","Smudge stick","Sow thistles","Dock","Artemisia abrotanum","Spearmint","Scilla","Stevia","Suma root","Summer savory","Sutherlandia frutescens","Sweet Grass","Galium odoratum","Tacamahac","Tandoori masala","Tansy","Tea","Felty germander","Thai basil","Thistle","Common Tormentil","Bindii","Ocimum tenuiflorum","Twinleaf onion","Arctostaphylos uva-ursi","Vasaka","Verbena","Chrysopogon zizanioides","Vietnamese coriander","Wattleseed","Wild ginger","Breckland thyme","Winter savory","Herb Bennett","Artemisia absinthium","Yarrow","Micromeria douglasii","Yohimbine","Artemisia princeps","Zedoary","Berbere","Five-spice powder","Garam masala","Herbes de Provence","Khmeli suneli","Adjika","Advieh","Afghan Spice Rub","Baharat","Bouquet garni","Buknu","Chaat masala","Chaunk","Chili powder","Crab boil","Fines herbes","Garlic salt","Harissa","Jamaican jerk spice","Lemon pepper","Masala","Mitmita","Mixed spice","Old Bay Seasoning","Pumpkin pie spice","Recado rojo","Shichimi","Tabil","Valencia orange","Sweetbread","Ris de veau","Malagueta pepper","Thousand Island dressing","Yemenite citron","Charcuterie","McIntosh","Ligonberry","Eastern Prickly Pear","Crab Apples","Empire Apples","Sorb Apple","Silver Buffaloberry","False-mastic","Sheepberry","Corned beef","Rocky Mountain oysters","Patagonian toothfish","Pistachio","Granny Smith","Fried onion","Cream of mushroom soup","Extra virgin olive oil","Noodle","Osake Kazu","Fauxtato","Absinthe","Beer","Coca-Cola","DDT","Gin","Rum","Soft drink","Stout","Sake","Sambuca","Sour mix","Vermouth","Vodka","Tequila","Bourbon whiskey","Brandy","Orange juice","Champagne","7 Up","Sugarcane","Red Bull","Rose water","Grenadine","Mezcal","Cognac","Tonic water","Moonshine","Sparkling wine","Pisco","Port wine","Akvavit","Irish whiskey","Ginger ale","Powdered sugar","Liebfraumilch","Galliano","Carbonated water","Kool-Aid","Herbsaint","Pastis","Triple sec","Ouzo","Rye whiskey","Bitters","Maraschino","Syrup","Chocolate liqueur","Half and half","Chartreuse","Tennessee whiskey","Egg white","Cachaca","Sloe gin","Baileys Irish Cream","Condensed milk","Cream soda","Lemonade","Orgeat syrup","Black tea","Apple juice","Egg yolk","Grand Marnier","Brown sugar","Amaretto","Apple cider","Irish cream","Tea leaf grading","Horchata","Ginger beer","Burgundy wine","Eggnog","Aguas frescas","Jim Beam","Cointreau","Tomato juice","Campari","Pimm's","Clamato","Hot sauce","Falernum","Light rum","Limoncello","Southern Comfort","Bacardi 151","Drambuie","WKD Original Vodka","Crown Royal","Hpnotiq","Grapefruit juice","Gordon's Gin","Angostura bitters","Muscovado","Malibu Rum","Benedictine","Midori","Fernet","Noilly Prat","Pomegranate juice","Lillet","Cruzan Rum","Lemon-lime","Guinness","Lichido","Dubonnet","Cyprus brandy","Orange bitters","Vanilla extract","Orange Flower Water","Applejack","La Casera","Red Wine","White Wine","Seagram's Seven Crown","Peychaud's Bitters","Celery salt","Coffee liqueur","Cranberry juice","Lime Juice","Dark Rum","Sazerac Rye Whiskey","Lemon disk","Heering Cherry Liqueur","White Rum","Apricot brandy","Papaya Juice","Golden Rum","Pineapple Juice","Cashew Juice","Cashew Slice","Sweet Red Vermouth","Dry Vermouth","Gomme syrup","Sirop de Fraise","Sweet Vermouth","Kumel","Sugar Syrup","Sugar Cube","Peach Brandy","Jamaican Amber Rum","Almond flavored syrup","Orange Liqueur","Passion Fruit Syrup","Guava juice","Mint leaf","Vanilla Ice Cream","Coconut cream","PAMA pomegranate flavoured liquor","Red Food Coloring","Blackberry Brandy","Margarita mix","Banana liqueur","Apple Schnapps","Cherry Liqueur","Beef bouillon","Blue Curacao","Apple Vodka","Peach schnapps","Carbonated orange drink","Passion Fruit Juice","Honey Liqueur","Peach bitters","Peach puree","Cherry Brandy","Sliced fruit","Fraise de Bois liqueur","Fruit juice","Sweet and sour mix","Amaretto Almond liqueur","Melon liqueur","Picon","Schlichte","Carpano","Dry White Wine","Fruit punch","Raspberry liqueur","Green mint syrup","Peppermint schnapps","Apple Pucker","Aromatic bitters","Yellow Chartreuse","Cypriot lemon squash","Vegetable extract","Wolfschmidt Kummel","Oil","Twinkie","Mozzarella","Brown rice","Basmati","Wehani rice","Jasmine rice","Fermented bean curd","Peanut oil","Canola Oil","Margarine","Copha","Cocoa bean","Chocolate chip","Molasses","Golden syrup","Demerara","Wheat gluten","Tempeh","Lemon peel","Blue cheese","Cream cheese","Balsamic vinegar","Vanilla essence","Corn starch","Rice flour","Cornmeal","Hominy","Spelt","Rye flour","Wild rice","Puy lentil","Peanut butter","Sesame seed","Poppy seed","Sunflower seed","Sunflower oil","Grape seed oil","Sesame oil","safflower oil","Tartaric acid","Citric acid","Dashi","Stick","Table sugar","Unsalted Butter","Graham flour","All-purpose Flour","Rolled oats","White Crab Mushroom","Salsa verde","Cheddar cheese","Quinoa","Nutritional yeast","American cheese","Arrowroot","Chia","Black bean paste","Pinole","Mud","Snickers","Escolar","Fishcake","Salumi","Peperoncini","Provolone","Prosecco","Aperol","Becherovka","Mirin","Yellowtail amberjack","Japanese amberjack","Whole-wheat flour","Atta flour","Crawfish tails","Crab meat","Roux","Organic Bread Flour","Coarse sea salt","Raw Wheat Germ","Mascarpone","Stock","Red onion","Rice wine","Black bean and garlic","Snap pea","Crushed red pepper","Kosher Salt","Black peppercorn","Vegetable oil","Oyster sauce","Brine","Monosodium glutamate","Starch","Caramel color","Cooking oil","Shellfish","Italian sausage","Yellow onion","Clam","Gruyere cheese","Bacon Drippings","Savoy cabbage","Ricotta forte","Mussel","Agar","White truffle oil","Tortiglioni","Madeira wine","Spanish rice","Sour cream","Strained yogurt","Duck legs","Duck fat","White Wings Blackberry Sponge Pudding","Granola","Diced tomatoes","Pearl onion","Herb","Fingerling potato","Champignon","Gherkin","Daylily","Apple sauce","Shacha sauce","Siu haau sauce","Blue cheese dressing","Cocoa butter","Chocolate liquor","Cocoa solids","Sherry","Grated cheese","Buttered breadcrumbs","Caramel","Fondant","Gum base","Royal icing","Nonpareils","Sugar paste","Cereal germ","Palm syrup","Boston butt","Ataulfo","Maple sugar","Goat Milk","Apple","Maida flour","Wheat flour","Raw milk","Acorn","Cephalopod ink","Dijon mustard","Cooking spray","Sea salt","Dry mustard","Red bell pepper","Pine nut","Juice","Italian seasoning","Ground red pepper","Nut","Tabasco sauce","Ice","Ice cube","Seasoned salt","Hoisin sauce","Sauces","Seasoning","Cool Whip","Zest","Grated parmesan","Green chilies","Corn kernels","Oat","Panko","Cajun seasoning","Hazelnut","Poultry seasoning","Liquid smoke","Feta","Pie crust","Dendrobranchiata","Cookie","Whipped topping","Miniature marshmallow","Garnish","Soy milk","Hamburger bun","Lump crabmeat","Yellow cake mix","Marshmallow","Marinade","Cracker","Creole seasoning","Ground chuck","Quick-cooking oat","Teriyaki sauce","Ricotta","Splenda","Crushed ice","Yellow pepper","Ranch dressing","Club soda","Gelatin","Glaze","Cake Mix","Food coloring","Plain low-fat yogurt","Pizza sauce","Graham cracker","Pepperoni","Bisquick","Miracle Whip","Ground white pepper","Gorgonzola","Sweet pickle relish","Butterscotch chip","Sultana","Xanthan gum","Whisky","Wonton wrapper","Fast Green FCF","Pizza dough","Cremini mushroom","Cracked pepper","Corn flakes","Frozen corn kernel","Berry","Dried currant","Chili paste","Liqueur","Agave nectar","Tamari","Mace","Cereal","Adobo sauce","Ground mustard","Instant espresso powder","White cake mix","Mixed salad greens","Oat bran","Halibut","Greek yogurt","Jam","Enchilada sauce","Phyllo","Graham cracker crust","Pickling spice","Crescent roll","Pimiento","Poblano","Brown mustard","Saltine cracker","Ground round","Ritz Cracker","Yellow food coloring","Creole mustard","Portabella mushroom","Pitted dates","Dried chilli","Wild mushroom","Prune","Taco seasoning mix","Sweet chilli sauce","Cider","English mustard","Alfredo sauce","Cola","Kirsch","Dough","Pickling salt","Wholegrain mustard","Miso","Chuck roast","Chili-garlic sauce","Nutella","Plain fat-free yogurt","Catfish","Tilapia","Green bell pepper","Steel-cut oats","Canola","Barley Malt Extract","Avena","Ale","English porter","Bran","Bulgur","Bouillon","Durum","Einkorn wheat","Farro","Gluten","Hordeum","Malted milk","Brown rice syrup","Rye","Triticale","Emmer","Farina","Filler","Wheatberry","Wheat germ oil","Wheatgrass","Barley malt syrup","Malt flavoring","Khorasan wheat","Glutenin","Brown bread","Enriched flour","Tomat","Cracker meal","Malt vinegar","Sprouted wheat","Marsala wine","Budu","Kobe beef","Ricotta forte","Buffalo meat","Tilapia","Rose's Lime Juice","Caffeine","Gum arabic","Barley malt","Brewer's yeast","Yuzu","Chili oil","Harrison Cider Apple","Thai green curry paste","Bacon","Bacon bits","roasted garlic cloves","garlic cloves","Freshly ground black pepper","Ground black pepper","black pepper","Scallions","minced beef","Natural brown sugar","Anise seed","Tomato puree","Tomato paste","Pleurotus eryngii","Oyster Mushroom","Stewed tomatoes","chopped fresh thyme leaves","Thyme leaves","dried thyme","Cinnamon stick","Ground cinnamon","Yukon Gold potato","Russet Burbank potato","salted butter","coarsely grated cheddar","grated cheddar","High-fructose corn syrup","Pepper","chopped green onions","low sodium soy sauce","Soy Sauce","mushroom flavored dark soy sauce","dark soy sauce","lite soy sauce","Sweetener","Soybean oil","Tripe","Zhug","Salt","Rib eye steak","Goat meat","Collagen","Turkey meat","Dog meat","Horse meat","Iguana meat","Duck meat","Ostrich meat","Quail meat","Flour tortilla","White rice","Pandan Rice","Wheat noodles","Guinea Fowl","Lime Leaf","Sirloin tip","Western griller","Flat Iron steak","Beef brain","Lamb brain","Loin Country-Style Ribs","Beef Round Top (Inside) Round Steak","Vegetable Oil","Palm oil","Coconut oil","Carbohydrate","Readily digestible starch","Resistant starch","Smoked paprika","Pimenton","Evaporated milk","Jack Daniel's","Jameson Irish Whiskey","Saba banana","T550 flour","T450 flour","Italian 00 flour","Italian 0 flour","Italian 1 flour","Italian 2 flour","Italian Integrale flour","Bread Flour","Farine de meule (T1100)","Farine de meule (T850)","Farine de seigle","T45 flour","T55 flour","Harina especial para freir","Campaillou","English organic wholemeal flour","Granary flour","Odium's Irish cream flour","Churchill strong white flour","Doves Farm organic strong white flour","Unbleached All-purpose flour","Bleached All-purpose flour","Unbleached Bread Flour","Poolish","Levain","Canadian flour","Hard red spring wheat","Wholemeal flour","Baker's yeast","Instant Yeast","SAF Perfect Rise Gourmet Yeast","Cake flour","Gold Medal Organic Unbleached Flour","SAF Traditional Active Dry Perfect Rise Yeast","White Self-rising Cornmeal","Amaranth flour","Millet flour","Self-rising flour","Light Rye flour","Medium Rye flour","Dark Rye flour","Mesquite flour","Mesquite","Teff flour","Teff","Buckwheat flour","Buckwheat","Malthouse flour","Almond meal","Emmer flour","Einkorn flour","Curly Parsley","Flat leaf Parsley","Dried Apple","Dried Apricots","Cassava flour","Chestnut flour","King Arthur Unbleached Bread Flour flour","King Arthur European-Style Artisan Bread Flour","Spelt flour","Acorn flour","Straight flour","King Arthur Sir Lancelot Unbleached Hi-Gluten Flour","Mushroom","Bass","Aspartame","Saccharin","Sheep","Macadamia nut","Fleur de sel","Sel gris","Flake salt","Alaea salt","Kala Namak","Maldon sea salt","Halen Mon - Smoked Sea Salt","Velvet De Guerande - by Le Tresor","Cyprus Black Lava Salt","Atlantic Spanish mackerel","9x Amethyst Bamboo salt","Black Truffle salt","Iburi-Jio Cherry salt","Maboroshi Plum salt","sel gris de I'lle de Noirmoutier","Saffron salt","Shinkai deep sea salt","Maine apple smoked salt","Japanese Nazuma salt","Papohaku white salt","Trapani salt","Aguni Koshin Odo salt","Ako Arashio salt","Cornish sea salt","Sal Rosa de Maras","Himalayan pink salt","Green Peppercorn","Pink peppercorn","dried Szechuan pepper","pickled peppercorns","dried mixed (Rainbow) peppercorns","Fructose malabsorption","Bacardi rum","Flax seed","Linseed oil","Bacardi Superior","Lime wedge","Chimichurri","Quorn","Fusarium venenatum","Smoked salt","Turkish Black Pyramid Sea Salt","Danish Viking salt","Boneless Skinless Chicken Thighs","Chicken Thighs","Chicken breast","Boneless Skinless Chicken Breast","Chicken stock","Beef stock","Fresh cilantro leaves","Eggplant","English cucumber","Fresh dill leaves","Cilantro leaves","Dried cilantro leaves","Cilantro","Lecithin","Pectin","Gomashio","Gochujang","Steamed rice","Oenanthe javanica","Enokitake","Tomato sauce","Georges Bank scallops","mouton","Legume","Panela","Whey","Poached egg","Buttercream","Scampi","Mirepoix","Rayu","Camellia sinensis","Ice chips","Batter","Fish"]

    items = sorted(items)


    for item in items:
        Ingredient.objects.get_or_create(ingredientName = item)
def add_measurement_units():
    items = ["Gallon (US)","Kilogram","Liter","Pound","Teaspoon","Tablespoon","Ounce","Pint (US)","Quart (US)","Fluid ounce (US)","Head","Dessert spoon","Cup","Gill","Pinch","Sachet","Jigger","Gram","Milliliter","Gallon (Imperial)","Fluid ounce (imperial)","Quart (Imperial)","Cubic centimetre","Dash","Tablespoon (AU)","Cup (Imperial)","Cup (Metric)","Cup (US)","Cup (Japan)","Pint (US dry)","Pint (metric)","Quart (US dry)","Gallon (US dry)","Gill (Imperial)","Centiliter","strips","Sprig","Bunch","clove","mL","mL","Cloves"]

    items = sorted(items)

    for item in items:
        MeasurementUnit.objects.get_or_create(measurementUnitName = item)
