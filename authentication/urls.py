from django.urls import include, path

from .views import LoginView, SignUpView, ProfileView
urlpatterns = [
    path(
        'signup',
        SignUpView.as_view(),
        name='signup'
    ),
    path(
        'login',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'profile',
        ProfileView.as_view(),
        name='profile'
    ),

]
