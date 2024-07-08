from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import *


class NewPostForm(forms.Form):
    content = forms.CharField(label="",
                              widget=forms.Textarea(attrs={"placeholder":"New Post"}))


def index(request):
    posts = Post.objects.all()

    return render(request, "network/index.html", {
        "posts": posts,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def new_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]

            post = Post(poster=request.user,
                        content=content,
                        like_count=0)
            
            post.save()

            # redirect to index
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/new.html", {
            "form": NewPostForm(),
        })
    

def user_page(request, name):
    user = User.objects.get(username=name)
    posts = Post.objects.filter(poster=user)

    return render(request, "network/user.html", {
        "posts": posts,
        "name": user.username,
        "followers": 0,
        "following": 0,
        "owner": user == request.user,
    })