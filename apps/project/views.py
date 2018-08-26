# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from helpmedoshit import settings
from models import *
import bcrypt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

#Stripe
def checkout(request, task_id):

    if request.method != "POST":
        redirect('/home')

    token = request.POST.get("stripeToken")
    task = Task.objects.get(id=task_id)
    payment = Pay.objects.get(task=task)

    try:
        charge  = stripe.Charge.create(
            amount      = int(task.price) * 100,
            currency    = "usd",
            source      = token,
            description = task.title
        )

        payment.stripe_charge_id = charge.id
        payment.status = 1
        payment.save()
        
    except stripe.error.CardError as ce:
        return False, ce

    else:
        return redirect("/user/{}".format(request.session['id']))
        # The payment was successfully processed, the user's card was charged.

#Registration/Login Page
def index(request):

    if 'id' in request.session:
        return redirect('/home')

    return render(request, 'project/index.html')

#Home Page
def home(request):

    if not 'id' in request.session:
        return redirect('/')

    user = User.objects.get(id=request.session['id'])
    context = {
        'logged_user': User.objects.get(id=request.session['id']),
        'available_tasks': Task.objects.exclude(uploaded_by=user).exclude(status="1"), #Status 1 means task has accepted bidder
    }

    return render(request, 'project/home.html', context)

#Logout
def logout(request):

    request.session.clear()
    return redirect('/')

#User pages
def user_profile(request, user_id):

    if not 'id' in request.session:
        return redirect('/')

    current_user = User.objects.get(id=request.session['id'])
    page_user = User.objects.get(id=user_id)
    #Status 2 means task is complete
    payments_to_make = Task.objects.filter(uploaded_by=current_user, status=2)

    print "Strike api key: "
    print settings.STRIPE_PUBLIC_KEY

    for payment in payments_to_make:
        payment.stripe_price = int(payment.price) * 100

    #If going to logged in user's page
    if page_user == current_user:
        context = {
            'logged_user': current_user,
            'getting_help_tasks': Task.objects.filter(uploaded_by=current_user, status='1'), #Status 1 means task has accepted bidder
            'uploaded_tasks': Task.objects.filter(uploaded_by=current_user, status=0), #Status 0 means task is available
            'my_offers': Task.objects.exclude(uploaded_by=current_user).filter(users_bidded=current_user, status=0),
            'my_accepted_offers': Task.objects.filter(users_bidded=current_user).filter(status='1'),
            'payments_to_make': payments_to_make,
            "stripe_key": settings.STRIPE_PUBLIC_KEY
        }
        
        return render(request, 'project/user_profile.html', context)

    #If going to some other user's page
    else: 
        context = {
            'profile_user': page_user,
            'uploaded_tasks': Task.objects.filter(uploaded_by=page_user),
            'logged_user': current_user
        }

        return render(request, 'project/foreign_user_page.html', context)

#Delete task process
def delete_task(request, task_id):

    if not 'id' in request.session:
        return redirect('/')

    Task.objects.get(id=task_id).delete()

    return redirect('/user/{}'.format(User.objects.get(id=request.session['id']).id))
    
#Process to bid on a task
def bid_task(request, task_id):

    if not 'id' in request.session:
        return redirect('/')

    current_task = Task.objects.get(id=task_id)
    #Adding bid
    current_task.users_bidded.add(User.objects.get(id=request.session['id']))
    current_task.save()

    return redirect('/home')

#Process to remove a bid 
def remove_bid(request, task_id):

    if not 'id' in request.session:
        return redirect('/')

    current_task = Task.objects.get(id=task_id)
    #Removing bid
    current_task.users_bidded.remove(User.objects.get(id=request.session['id']))
    current_task.save()

    return redirect('/home')

#Accept an offer
def accept_offer(request, task_id, offering_id):

    if not "id" in request.session:
        return redirect('/')

    current_user = User.objects.get(id=request.session['id'])
    
    task = Task.objects.get(id=task_id)
    #Task has helper
    task.status = 1
    #Set helper
    task.accepted_helper = User.objects.get(id=offering_id)
    task.save()

    return redirect('/user/{}'.format(request.session['id']))

#Mark a task complete
def mark_as_completed(request, task_id):

    if not "id" in request.session:
        return redirect('/')

    print 'hello from mark_as_completed'


    current_user = User.objects.get(id=request.session['id'])
    task = Task.objects.get(id=task_id)
    #Remove offers
    task.users_bidded.clear()
    #Task is complete
    task.status = 2
    task.save()

    #Create a pay object with status = 0 (not complete)
    Pay.objects.create(task=task, pay_from=current_user, pay_to=task.accepted_helper, amount=task.price)

    return redirect('/user/{}'.format(request.session['id']))


def decline_offer(request, task_id, offering_id):

    if not "id" in request.session:
        return redirect('/')

    task = Task.objects.get(id=task_id)
    #Decline offer, remove from many to many relationship
    task.users_bidded.remove(User.objects.get(id=offering_id))

    return redirect('/user/{}'.format(request.session['id']))

def cancel_work_agreement(request, task_id):

    if not "id" in request.session:
        return redirect('/')

    task = Task.objects.get(id=task_id)

    #Remove user helping
    task.accepted_helper = None
    #Task is available 
    task.status = 0
    #Remove all relationships between task and its previous offers
    task.users_bidded.clear()
    task.save()

    return redirect('/user/{}'.format(request.session['id']))

def view_task(request, task_id):

    if not "id" in request.session:
        return redirect('/')

    context = {
        'current_task': Task.objects.get(id=task_id),
        'logged_user': User.objects.get(id=request.session['id'])
    }

    return render(request, 'project/task.html', context)

# POST # POST # POST # POST # POST # POST # POST # POST # POST # POST # POST # POST 
# =============================================================================

#Register
def register(request):

    if request.method == "POST":

        #If errors present
        errors = User.objects.reg_validator(request.POST)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')

        #If successful 
        hp = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        #Create user
        user = User.objects.create(name=request.POST['name'], email=request.POST['email'], username=request.POST['username'], password=hp, zip_code=request.POST['zip'])
        request.session['id'] = user.id

        return redirect('/home')

#----------

#Login
def login(request):

    if request.method != "POST":
        redirect('/home')

    #If errors
    errors = User.objects.login_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        return redirect('/')

    #If successful, add user to session
    request.session['id'] = User.objects.get(username=request.POST['username']).id
    return redirect('/home')

#----------

#Create task process
def add_task_process(request):

    if request.method != "POST":
        redirect('/home')

    #If errors creating task
    errors = Task.objects.task_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        return redirect('/task/add')

    #If there is an image
    try:
        Task.objects.create(title=request.POST['title'], description=request.POST['description'], price=request.POST['pay'], image=request.FILES['image'], uploaded_by=User.objects.get(id=request.session['id']), zip_code=request.POST['zip_code'])
        return redirect('/user/{}'.format(request.session['id']))
    #If there is no image
    except:
        Task.objects.create(title=request.POST['title'], description=request.POST['description'], price=request.POST['pay'], uploaded_by=User.objects.get(id=request.session['id']), zip_code=request.POST['zip_code'])
        return redirect('/user/{}'.format(request.session['id']))
        
#----------

#Editing tasks
def edit_task_process(request, task_id):

    if request.method != "POST":
        redirect('/home')

    #If errors
    errors = Task.objects.task_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        return redirect('/task/edit/{}'.format(task.id))
    
    #Reassign task attributes
    task = Task.objects.get(id=task_id)
    task.title=request.POST['title'] 
    task.description=request.POST['description']
    task.price=request.POST['pay']

    #Handle image
    try:
        task.image=request.FILES['image']
    except:
        pass

    task.uploaded_by=User.objects.get(id=request.session['id'])
    task.zip_code=request.POST['zip_code']
    task.save()

    return redirect('/user/{}'.format(request.session['id']))

#----------

#To do
def admin_login(request):
    return redirect('/')

#----------

#Edit user process
def edit_user_process(request, user_id):

    if request.method != "POST":
        redirect('/home')

    user = User.objects.get(id=user_id)

    #If errors while editing
    errors = User.objects.edit_validator(request.POST, user)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags = tag)
        return redirect('/user/{}/edit'.format(request.session['id']))

    #If no errors, edit user attributes
    user = User.objects.get(id=user_id)
    user.name = request.POST['name']
    user.username = request.POST['username']
    user.email = request.POST['email']
    user.zip_code = request.POST['zip_code']

    #Handle images
    try:
        user.image = request.FILES['image']        
    except:
        pass

    user.save()

    return redirect('/user/{}'.format(user_id))