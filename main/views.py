# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.models import UserForm, UserProfile
from recipe_project.settings import STATIC_URL

def main_page(request):
    d = {"user" : request.user}
    return render_to_response('main_page.html', d)


def register(request):
    if request.method == 'POST':
        formset = UserForm(request.POST, request.FILES)
        if formset.is_valid():
            newUser =  User.objects.create_user(formset.data['username'], formset.data['email'], formset.data['password'])
            custom = UserProfile(user = newUser)
            custom.user_id = newUser.id
            custom.save()
            newUser = authenticate(username=request.POST['username'],password=request.POST['password'])
            login(request, newUser)

            return render_to_response("registration/register_success.html")
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
    d = {"user" : request.user}
    return render_to_response('profile.html', d)
@login_required
def create_view(request):
    d = {"user" : request.user}
    return render_to_response('create.html', d)