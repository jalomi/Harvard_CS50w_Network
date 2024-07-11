
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_post, name="new"),
    path("following", views.following, name="following"),
    path("user/<str:name>", views.user_page, name="user"),
    path("follow/<str:name>", views.follow, name="follow"),
    path("edit/<int:id>", views.edit_post, name="edit"),
]
