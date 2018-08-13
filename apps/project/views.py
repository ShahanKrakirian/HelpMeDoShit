# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from models import *
import bcrypt

def index(request): #Registration

    if 'id' in request.session: #if logged in
        return redirect('/home')
    return render(request, 'project/index.html')

def login(request): 

    if 'id' in request.session: #if logged in
        return redirect('/home')
    return render(request, 'project/login.html')

def home(request): #Home

    if not 'id' in request.session: #if not logged in
        return redirect('/')
    user = User.objects.get(id=request.session['id'])
    context = {
        'logged_user': User.objects.get(id=request.session['id']),
        'available_tasks': Task.objects.exclude(uploaded_by=user),
    }
    return render(request, 'project/home.html', context)

def logout(request): #Logout

    request.session.clear()
    return redirect('/')

def admin(request): #Admin 

    return render(request, 'project/admin_login.html')

def user_profile(request, user_id): #User_Profile

    if not 'id' in request.session: # if not logged in
        return redirect('/')

    current_user = User.objects.get(id=request.session['id'])
    page_user = User.objects.get(id=user_id)

    if page_user == current_user:
        context = {
            'logged_user': current_user,
            'uploaded_tasks': Task.objects.filter(uploaded_by=current_user),
            'pending_tasks': User.objects.get(id=user_id).tasks.all()
        }
        
        return render(request, 'project/user_profile.html', context)

    else: 
        context = {
            'profile_user': page_user,
            'uploaded_tasks': Task.objects.filter(uploaded_by=page_user),
        }

        return render(request, 'project/foreign_user_page.html', context)

def add_task(request): #Add_Task

    if not 'id' in request.session: # if not logged in
        return redirect('/')
    return render(request, 'project/add_task.html')

def delete_task(request, task_id): #Delete_Task

    if not 'id' in request.session:
        return redirect('/')
    Task.objects.get(id=task_id).delete()
    return redirect('/user/{}'.format(User.objects.get(id=request.session['id']).id))

def edit_task(request, task_id):

    if not 'id' in request.session:
        return redirect('/')
    context = {
        'task': Task.objects.get(id=task_id)
    }
    return render(request, 'project/edit_task.html', context)
    
def bid_task(request, task_id):

    if not 'id' in request.session:
        return redirect('/')
    current_task = Task.objects.get(id=task_id)
    current_task.users_bidded.add(User.objects.get(id=request.session['id']))
    current_task.save()
    print current_task.users_bidded.all()

    return redirect('/home')

def remove_bid(request, task_id):

    if not 'id' in request.session:
        return redirect('/')
    current_task = Task.objects.get(id=task_id)
    current_task.users_bidded.remove(User.objects.get(id=request.session['id']))
    current_task.save()
    print current_task.users_bidded.all()

    return redirect('/home')

def edit_user(request, user_id):

    if not "id" in request.session:
        return redirect('/')

    context = {
        'user': User.objects.get(id=user_id)
    }
    
    return render(request, 'project/edit_profile.html', context)

def accept_offer(request, task_id, offering_id):

    if not "id" in request.session:
        return redirect('/')
    
    task = Task.objects.get(id=task_id)
    task.status = 1
    task.save()

# POST # POST # POST # POST # POST # POST # POST # POST # POST # POST # POST # POST 
# =============================================================================

def register(request): #Register

    if request.method == "POST": #if post

        errors = User.objects.reg_validator(request.POST) #if failed reg
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')

        hp = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()) #successful reg
        user = User.objects.create(name=request.POST['name'], email=request.POST['email'], username=request.POST['username'], password=hp, zip_code=request.POST['zip'])
        request.session['id'] = user.id
        Cart.objects.create(user=user) 
        return redirect('/home')

#----------

def login(request): #Login

    if request.method == "POST": #if post

        errors = User.objects.login_validator(request.POST) #if errors
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')

        request.session['id'] = User.objects.get(username=request.POST['username']).id #successful login
        return redirect('/home')

#----------

def add_task_process(request):

    if request.method == "POST": # if post

        errors = Task.objects.task_validator(request.POST) #if errors
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/task/add')

        try:
            Task.objects.create(title=request.POST['title'], description=request.POST['description'], price=request.POST['pay'], image=request.FILES['image'], uploaded_by=User.objects.get(id=request.session['id']), zip_code=request.POST['zip_code'])
            return redirect('/user/{}'.format(request.session['id']))
        except:
            Task.objects.create(title=request.POST['title'], description=request.POST['description'], price=request.POST['pay'], uploaded_by=User.objects.get(id=request.session['id']), zip_code=request.POST['zip_code'])
            return redirect('/user/{}'.format(request.session['id']))
        
#----------

def edit_task_process(request, task_id):

    if request.method == "POST": #if post
        errors = Task.objects.task_validator(request.POST) #if errors 
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/task/edit/{}'.format(task.id))
        
        task = Task.objects.get(id=task_id)
        task.title=request.POST['title'] 
        task.description=request.POST['description']
        task.price=request.POST['pay']
        try:
            task.image=request.FILES['image']
        except:
            pass
        task.uploaded_by=User.objects.get(id=request.session['id'])
        task.zip_code=request.POST['zip_code']
        task.save()
        return redirect('/user/{}'.format(request.session['id']))

#----------

def admin_login(request): #Admin_Login
    return redirect('/')

#----------

def edit_user_process(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        errors = User.objects.edit_validator(request.POST, user)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags = tag)
            return redirect('/user/{}/edit'.format(request.session['id']))

    user = User.objects.get(id=user_id)
    user.name = request.POST['name']
    user.username = request.POST['username']
    user.email = request.POST['email']
    user.zip_code = request.POST['zip_code']
    try:
        user.image = request.FILES['image']        
    except:
        pass
    user.save()
    return redirect('/user/{}'.format(user_id))