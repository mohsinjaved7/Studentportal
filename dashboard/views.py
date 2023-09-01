import bs4
from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
from pydictionary import Dictionary
import json
import wikipedia
import requests
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def HOME(request):
    return render(request,'dashboard/home.html')


@login_required
def NOTES(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
            messages.success(request,f"Notes Added from {request.user.username} Successfully!")
            return redirect('notes')
    else:
        form=NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {
        'notes':notes,
        'form':form,
    }
    return render(request,'dashboard/notes.html',context)


@login_required
def DELETE_NOTE(request,pk=None):
    notes = Notes.objects.get(id=pk)
    notes.delete()
    return redirect('notes')



class NotesDetailView(generic.DetailView):
    model = Notes


@login_required
def homework(request):
    if request.method == "POST":
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
                is_finished=finished
            )
            homeworks.save()
            messages.success(request,f"Homework added from {request.user.username}!")
            # return redirect('homework')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {
        'homework': homework,
        'homework_done': homework_done,
        'form': form,
    }
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def Delete_Homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    homework.delete()
    return redirect('homework')


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnail': i['thumbnails'][0]['url'],
                'channel': i['channel']['name'],
                'link': i['link'],
                'views': i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context = {
                'form': form,
                'results': result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form = DashboardForm()
    context ={
        'form':form,
    }
    return render(request,'dashboard/youtube.html',context)

@login_required
def todo(request):
    if request.method == "POST":
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
            messages.success(request,f'Task Added by {request.user.username}!')
            return redirect('todo')
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context ={
        'form':form,
        'todos':todo,
        'todos_done':todos_done,
    }
    return render(request,'dashboard/todo.html',context)

@login_required
def update_todo(request,pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished:
        todo.is_finished=False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')


@login_required
def Delete_Todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')


@login_required
def Books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            context = {
                'form': form,
                'results': result_list,
            }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    context = {
        'form': form,
    }
    return render(request, 'dashboard/books.html', context)



def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://dictionary-by-api-ninjas.p.rapidapi.com/v1/dictionary"
        headers = {
            "X-RapidAPI-Key": "4ea5d76b95msh8ae9cad8c366906p1e8c51jsnef3e8d48a7fc",
            "X-RapidAPI-Host": "dictionary-by-api-ninjas.p.rapidapi.com"
        }
        r = requests.get(url,headers)
        answer = r.json

        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except:
            context ={
                'form': form,
                'input': ''
            }
        return render(request,'dashboard/dictionary.html',context)
    else:
        form = DashboardForm()
    context = {
        'form': form,
    }
    return render(request,'dashboard/dictionary.html',context)



def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form': form,
            'title': search.title,
            'link': search.url,
            'details': search.summary
        }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
    context = {
         'form': form,
    }
    return render(request, 'dashboard/wiki.html', context)


@login_required
def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'
                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                    'answer': answer
                }
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)/2.20462} pound'
                context = {
                    'form': form,
                    'm_form': measurement_form,
                    'input': True,
                    'answer': answer
                }
    else:
        form = ConversionForm()
        context = {
            'form': form,
            'input': False
        }
    return render(request,'dashboard/conversion.html',context)



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account created for {username} Successfully!")
            return redirect('login')
    else:
         form = UserCreationForm()
    context ={'form':form }
    return render(request,'dashboard/register.html',context)


@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context ={
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todos_done':todos_done
    }
    return render(request,'dashboard/profile.html',context)


def Search(request):
    word = request.GET['word']

    res = requests.get('https://www.dictionary.com/browse/' + word)
    res2 = requests.get('https://www.thesaurus.com/browse/' + word)

    if res:
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        meaning = soup.find_all('ol', {'start': '1'})
        meaning1 = meaning[0].getText()
    else:
        word = 'Sorry, ' + word + ' Is Not Found In Our Database'
        meaning = ''
        meaning1 = ''

    if res2:
        soup2 = bs4.BeautifulSoup(res2.text, 'lxml')

        synonyms = soup.find_all('td', {'class': 'MS3LWmychBIpSUnRRwv_'})
        ss = []
        for b in synonyms[0:]:
            re = b.text.strip()
            ss.append(re)
        se = ss

        antonyms = soup2.find_all('a', {'class': 'Cil3vPqnHSU3LLCTZ62n c2bTkbyZ6pxWgWJDxVMX nqaIr5nC4kceBVw8A7mF'})
        aa = []
        for c in antonyms[0:]:
            r = c.text.strip()
            aa.append(r)
        ae = aa
    else:
        se = ''
        ae = ''

    results = {
        'word': word,
        'meaning': meaning1,
    }

    return render(request, 'dashboard/search.html', {'se': se, 'ae': ae, 'results': results})