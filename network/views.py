from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import *


class NewPostForm(forms.Form):
    content = forms.CharField(label="",
                              widget=forms.Textarea(attrs={"placeholder":"New Post"}))
    
class NewFollowerForm(forms.Form):
    pass


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    page = Paginator(posts, 10).get_page(request.GET.get('page'))

    return render(request, "network/index.html", {
        "page_obj": page,
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
    posts = Post.objects.filter(poster=user).order_by("-timestamp")
    page = Paginator(posts, 10).get_page(request.GET.get('page'))

    followers = Follow.objects.filter(following=user)
    following = Follow.objects.filter(follower=user)

    is_following = False
    owner = False
    is_auth = False
    if request.user.is_authenticated:
        is_following = followers.filter(follower=request.user).exists()
        owner = user == request.user
        is_auth = True

    return render(request, "network/user.html", {
        "page_obj": page,
        "username": user.username,
        "followers": followers.count(),
        "following": following.count(),
        "is_auth": is_auth,
        "owner": owner,
        "is_following": is_following,
    })


def follow(request, name):
    if request.method == "POST":
        form = NewFollowerForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=name)
            try:
                follow = Follow.objects.get(following=user, follower=request.user)
                follow.delete()
            except Follow.DoesNotExist:
                new_follow = Follow(following=user,
                                    follower=request.user)
                
                new_follow.save()
    
    return HttpResponseRedirect(reverse("user", args=[name]))


def following(request):
    follows = Follow.objects.filter(follower=request.user)

    posts = Post.objects.none()

    for f in follows:
        p = Post.objects.filter(poster=f.following)
        posts = posts | p

    posts = posts.order_by("-timestamp")
    page = Paginator(posts, 10).get_page(request.GET.get('page'))

    return render(request, "network/following.html", {
        "page_obj": page,
    })