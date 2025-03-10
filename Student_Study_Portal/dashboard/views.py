from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from .models import Notes
from youtubesearchpython import VideosSearch 
import requests
# Create your views here.
def home(request):
    return render(request,'home.html')
def notes(request):
    if request. method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f'Notes added from {request.user.username} successfully')
    else:
        
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request,'notes.html',context)

def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('notes')

class NotesDetailView(generic.DetailView):
    model = Notes
    template_name = 'notes_detail.html'
    context_object_name = 'note'
    
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
                homeworks = Homework(
                    user=request.user,
                    subject=request.POST['subject'],
                    title=request.POST['title'],
                    description=request.POST['description'],
                    due=request.POST['due'],
                    is_finished=finished)
                homeworks.save()
                messages.success(request,f'Homework added from {request.user.username} successfully!!')
    else:
                
                form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
         homework_done = True
    else:
        homework_done = False
    context = {'homeworks':homework,'homeworks_done':homework_done,'form':form}
    return render(request,'homework.html',context)


def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')


def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')

def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['results']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'channel':i['channel']['name'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {'form':form,
                       'results':result_list
            }          
        return render(request,'youtube.html',context)
    else:
        
        form = DashboardForm()
    context = {'form':form}
    return render(request,'youtube.html',context)

def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
                
            )
            todos.save()
            messages.success(request,f'Todo added from {request.user.username} successfully!!')
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
         todos_done = True
    else:
        todos_done = False
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,'todo.html',context)

def update_todo(request,pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')

def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://www.googleapis.com/books/v1/volumes?q='+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLinks'),
                
            }
            result_list.append(result_dict)
            context = {'form':form,
                       'results':result_list
            }          
        return render(request,'books.html',context)
    else:
        
        form = DashboardForm()
    context = {'form':form}
    return render(request,'books.html',context)

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en_US'+text
        r = request.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics']['text']
            audio = answer[0]['phonetics']['audio']
            definition = answer[0]['meanings']['definitions'][0]['definition']
            example = answer[0]['meanings']['definitions'][0]['examples']
            synonyms = answer[0]['phonetics']['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input': text,
                'phonetics': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms
            }
        except:
            context = {
                'form':form,
                'input':''
            }
        return render(request,'dictionary.html',context)
    else: 
        form = DashboardForm()
    context = {'form':form}
    return render(request,'dictionary.html',context)



    