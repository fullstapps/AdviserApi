from django.urls import include, path

from .views import RequestMessageView, MessageListView
urlpatterns = [
    path(
        'request',
        RequestMessageView.as_view(),
        name='signup'
    ),
    path(
        'list',
        MessageListView.as_view(),
        name='signup'
    ),

]

