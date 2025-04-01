from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from .models import Notes
from youtubesearchpython import VideosSearch 
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
from wikipedia.exceptions import DisambiguationError
from googleapiclient.discovery import build

# Create your views here.
def home(request):
    return render(request,'home.html')

@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(request, f'Notes added from {request.user.username} successfully')
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'notes.html', context)

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
                finished = finished == 'on'
            except KeyError:
                finished = False

            homeworks = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished,
            )
            homeworks.save()
            messages.success(request, f'Homework added from {request.user.username} successfully!!')
    else:
        form = HomeworkForm()

    homework = Homework.objects.filter(user=request.user)
    homework_done = len(homework) == 0

    context = {'homeworks': homework, 'homework_done': homework_done, 'form': form}
    return render(request, 'homework.html', context)


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
        api_key = 'AIzaSyBBIT1Ql5HSBQqZgCPlXDR0y1cE4tN0mcI'  # Replace with your actual API key
        youtube = build('youtube', 'v3', developerKey=api_key)
        try:
            # Perform a search query using the YouTube Data API
            search_response = youtube.search().list(
                q=text,
                part='snippet',
                maxResults=10
            ).execute()

            result_list = []
            for item in search_response.get('items', []):
                # Extract video details
                result_dict = {
                    'input': text,
                    'title': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'link': f"https://www.youtube.com/watch?v={item['id']['videoId']}" if item['id']['kind'] == 'youtube#video' else '#',
                    'channel': item['snippet']['channelTitle'],
                    'published': item['snippet']['publishedAt'],
                    'description': item['snippet'].get('description', 'N/A'),
                }
                result_list.append(result_dict)

            context = {'form': form, 'results': result_list}
        except Exception as e:
            # Handle errors gracefully
            context = {'form': form, 'error': f"An error occurred: {str(e)}"}
        return render(request, 'youtube.html', context)
    else:
        form = DashboardForm()
        return render(request, 'youtube.html', {'form': form})

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
        url = f'https://www.googleapis.com/books/v1/volumes?q={text}'
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(min(10, len(answer.get('items', [])))):
            item = answer['items'][i]['volumeInfo']
            result_dict = {
                'title': item.get('title'),
                'subtitle': item.get('subtitle'),
                'description': item.get('description'),
                'count': item.get('pageCount'),
                'categories': item.get('categories'),
                'rating': item.get('averageRating'),
                'thumbnail': item.get('imageLinks', {}).get('thumbnail'),
                'preview': item.get('previewLink'),
            }
            result_list.append(result_dict)
        context = {'form': form, 'results': result_list}
        return render(request, 'books.html', context)
    else:
        form = DashboardForm()
    return render(request, 'books.html', {'form': form})

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = f'https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}'
        r = requests.get(url)
        try:
            answer = r.json()
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'N/A')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
            definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'N/A')
            example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', 'N/A')
            synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except (IndexError, KeyError, TypeError):
            # Handle cases where the API response is invalid or missing data
            context = {
                'form': form,
                'input': text,
                'error': f"No results found for '{text}'. Please try another word.",
            }
        except Exception as e:
            # Handle other exceptions (e.g., network issues)
            context = {
                'form': form,
                'error': f"An error occurred: {str(e)}",
            }
        return render(request, 'dictionary.html', context)
    else:
        form = DashboardForm()
        return render(request, 'dictionary.html', {'form': form})

def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        try:
            search = wikipedia.page(text)
            context = {
                'form': form,
                'title': search.title,
                'links': search.links,
                'details': search.summary,
            }
        except DisambiguationError as e:
            # Handle disambiguation by showing the options
            context = {
                'form': form,
                'error': f"The term '{text}' is ambiguous. Please refine your search.",
                'options': e.options,  # List of possible options
            }
        except Exception as e:
            # Handle other exceptions
            context = {
                'form': form,
                'error': f"An error occurred: {str(e)}",
            }
        return render(request, 'wiki.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
    return render(request, 'wiki.html', context)

def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True,
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and int(input_value) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input_value} yard = {int(input_value) * 3} foot'
                    elif first == 'foot' and second == 'yard':
                        answer = f'{input_value} foot = {int(input_value) / 3} yard'
                context['answer'] = answer
        elif request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True,
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input_value = request.POST['input']
                answer = ''
                if input_value and int(input_value) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input_value} pound = {int(input_value) * 0.453592} kilogram'
                    elif first == 'kilogram' and second == 'pound':
                        answer = f'{input_value} kilogram = {int(input_value) * 2.20462} pound'
                context['answer'] = answer
    else:
        form = ConversionForm()
        context = {'form': form, 'input': False}
    return render(request, 'conversion.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account created for {username} successfully')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context = {'form':form}
    return render(request,'register.html',context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    homework_done = len(homeworks) == 0
    todos_done = len(todos) == 0

    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done,
    }
    return render(request, 'profile.html', context)

