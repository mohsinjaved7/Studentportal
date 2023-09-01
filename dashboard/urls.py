from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('',views.HOME,name='home'),
    path('notes',views.NOTES,name='notes'),
    path('delete_note/<int:pk>',views.DELETE_NOTE,name='delete_note'),
    path('notes_details/<int:pk>',views.NotesDetailView.as_view(),name='notes_details'),

    path('homework',views.homework,name='homework'),
    path('update_homework/<int:pk>',views.update_homework,name='update_homework'),
    path('delete_homework/<int:pk>',views.Delete_Homework,name='delete_homework'),

    path('youtube',views.youtube,name='youtube'),

    path('todo',views.todo,name='todo'),
    path('update_todo/<int:pk>',views.update_todo,name='update_todo'),
    path('delete_todo/<int:pk>',views.Delete_Todo,name='delete_todo'),

    path('books',views.Books,name='books'),

    path('dictionary',views.dictionary,name='dictionary'),
    path('search/',views.Search,name='search'),

    path('wiki',views.wiki,name='wiki'),

    path('conversion',views.conversion,name='conversion'),

]
