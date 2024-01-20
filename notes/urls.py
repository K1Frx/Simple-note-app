from django.urls import path
from .views import *

urlpatterns = [
    path('accounts/login/', SimpleLoginView.as_view(), name='login'),
    path('accounts/register/', SimpleRegisterView.as_view(), name='register'),
    path('my-notes/', NoteListView.as_view(), name='note_list'),
    path('', HomeRedirectView.as_view(), name='home'),
    path('accounts/logout/', simple_logout, name='logout'),
    path('note/<int:pk>/', NoteDetailView.as_view(), name='note_detail'),
    path('add-note/', NoteCreateView.as_view(), name='add_note')
]