from django.urls import path
from . import views
from .views import NotesDetailView

urlpatterns = [
    path('',views.home,name='home'),
    path('notes/',views.notes,name='notes'),
    path('delete_note/<int:pk>/',views.delete_note,name='delete_note'),
    path('notes_detail/<int:pk>/',NotesDetailView.as_view(),name='Notes_detail'),
]
