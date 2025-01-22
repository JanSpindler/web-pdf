from django.urls import path
from .views import session_detail, create_session


urlpatterns = [
    path('session/', create_session, name='create_session'),
    path('session/<int:id>', session_detail, name='session'),
]
