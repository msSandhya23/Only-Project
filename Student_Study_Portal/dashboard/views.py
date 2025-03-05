from django.shortcuts import render
from . forms import Notes,NotesForm
# Create your views here.
def home(request):
    return render(request,'home.html')
def notes(request):
    form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request,'notes.html')