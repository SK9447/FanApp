from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
import bcrypt

def index(request):
    if 'authenticator' not in request.session:
        return render(request, 'Fanapp/index.html')
    else:
        return redirect('/stories')

def stories(request):
    if 'authenticator' not in request.session:
        return render(request, 'Fanapp/hacker.html')
    else:
        context = {
            'user': User.objects.get(email_hash=request.session['authenticator']),
            'stories': User.objects.get(email_hash=request.session['authenticator']).stories.all(),
            'marked_stories': Marked_story.objects.all()
        }
        return render(request, 'Fanapp/stories.html', context)

def hacker(request):
    return render(request, 'Fanapp/hacker.html')

def new(request):
    if 'authenticator' not in request.session:
        return render(request, 'Fanapp/hacker.html')
    else:
        context = {
            'user': User.objects.get(email_hash=request.session['authenticator'])
        }
        return render(request, 'Fanapp/new.html', context)

def edit(request, id):
    if 'authenticator' not in request.session:
        return render(request, 'Fanapp/hacker.html')
    else:
        context = {
            'user': User.objects.get(email_hash=request.session['authenticator']),
            'story': Story.objects.get(id=id)
        }
        return render(request, 'Fanapp/edit.html', context)

def stats(request):
    if 'authenticator' not in request.session:
        return render(request, 'Fanapp/hacker.html')
    else:
        context = {
            'user': User.objects.get(email_hash=request.session['authenticator']),
            'marked_stories': Marked_story.objects.count(),
            'user_marked_stories': User.objects.get(email_hash=request.session['authenticator']).marked_stories.count(),
            'user_pending_stories': User.objects.get(email_hash=request.session['authenticator']).stories.count()
        }
        return render(request, 'Fanapp/stats.html', context)

def register(request):
    if request.method == 'POST':
        errors = User.objects.registration_validator(request.POST)
        if len(errors):
            for value in errors:
                messages.error(request, value, extra_tags='register')
            return redirect('/')
        else:
            create = User.objects.create_user(request.POST)
            messages.success(request, "User successfully created!")
            user = User.objects.last()
            request.session['authenticator'] = user.email_hash
            request.session['user_id'] = user.id
        return redirect('/stories')    
    else:
        return redirect('/')

def login(request):
    if request.method == 'POST':
        errors = User.objects.login_validator(request.POST)
        if len(errors):
            for value in errors:
                messages.error(request, value, extra_tags='login')
            return redirect('/')
        else:
            user = User.objects.get(email = request.POST['email'])
            request.session['authenticator'] = user.email_hash
            request.session['user_id'] = user.id
        return redirect('/stories')    
    else:
        return redirect('/')

def logout(request):
    if request.method == 'POST':
        request.session.clear()
        return redirect('/')
    else:
        return redirect('/')

def new_story(request):
    if request.method == 'POST':
        errors = Story.objects.story_validator(request.POST)
        if len(errors):
            for value in errors:
                messages.error(request, value)
            return redirect('/new')
        else:
            Story.objects.create(topic=request.POST['topic'], desc=request.POST['desc'], user=User.objects.get(id=request.POST['user_id']))
            return redirect('/stories')
    else:
        return redirect('/')

def mark(request):
    if request.method == 'POST':
        Marked_story.objects.create(topic=request.POST['story_topic'], user=User.objects.get(id=request.POST['user_id']), date_added=request.POST['story_created'])
        story = Story.objects.get(id=request.POST['story_id'])
        story.delete()
        return redirect('/stories')
    else:
        return redirect('/')

def update(request, id):
    if request.method == 'POST':
        errors = Story.objects.story_validator(request.POST)
        if len(errors):
           for value in errors:
                messages.error(request, value)
                return redirect('/edit/'+id)

        else:
            story = Story.objects.get(id= id)
            story.topic = request.POST['topic']
            story.desc = request.POST['desc']
            story.save()
            return redirect('/stories')    
    else:
        return redirect('/')

def like(request):
    if request.method == 'POST':
        marked = Marked_story.objects.get(id=request.POST['mark_id'])
        user = User.objects.get(id=request.POST['user_id'])
        if marked.user_id == user.id:
            messages.error(request, "Users may not like their own stories.")
            return redirect('/stories')
        if len(marked.likes.filter(id=request.POST['user_id'])) > 0:
            messages.error(request, "You have already liked this story.")
            return redirect('/stories')
        else:
            marked.likes.add(user)
            return redirect('/stories')

def delete(request, id):
    if request.method == 'POST':
        story = Story.objects.get(id=id)
        story.delete()
        return redirect('/stories')
    else:
        return redirect('/')

