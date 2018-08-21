# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import bcrypt
import re
import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]+$')

# Create your models here.

class UserManager(models.Manager):
    def reg_validator(self, postData):
        errors = {}
        if len(postData['name']) < 3:
            errors["name"] = "Name must be at least 3 characters." 
        if len(postData['username']) < 3:
            errors["username"] = "Username must be at least 3 characters." 
        if len(postData['email']) < 1 or not EMAIL_REGEX.match(postData['email']):
            errors["email_invalid"] = "Please enter a valid email."
        if postData['password'] != postData['confirm_password']:
            errors["pw_diff"] = "Passwords don't match."
        if len(postData['confirm_password']) < 8 or len(postData['password']) < 8:
            errors["pw_short"] = "Password must be at least 8 characters."
        if len(User.objects.filter(username = postData["username"])) > 0:
            errors["username_taken"] = "This username is not available."
        return errors

    def login_validator(self, postData):
        errors = {}
        try:
            User.objects.get(username=postData['username'])
            if not bcrypt.checkpw(postData['password'].encode(), User.objects.get(username=postData['username']).password.encode()):
                errors["incorrect_password"] = "Password is incorrect."
        except: 
            errors['username_DNE'] = "Username doesn't match anything in our records."
        return errors

    def edit_validator(self, postData, user):
        errors = {}
        if len(postData['name']) < 3:
            errors["name"] = "Name must be at least 3 characters." 
        if len(postData['username']) < 3:
            errors["username"] = "Username must be at least 3 characters." 
        if len(postData['email']) < 1 or not EMAIL_REGEX.match(postData['email']):
            errors["email_invalid"] = "Please enter a valid email."
        if len(User.objects.filter(username = postData["username"]).exclude(id=user.id)) > 0:
            errors["username_taken"] = "This username is not available."
        return errors
        

class TaskManager(models.Manager):
    def task_validator(self, postData):
        errors = {}
        if len(postData['title']) < 4:
            errors['title'] = "Title must be at least 4 characters."
        if len(postData['description']) < 10:
            errors['description'] = "Description must be at least 10 characters."
        return errors

class User(models.Model):
    name = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
    username = models.CharField(max_length = 50)
    password = models.CharField(max_length = 50)
    zip_code = models.CharField(max_length = 10)
    admin_status = models.SmallIntegerField(default = 0) # 0 = Not Admin | 1 = Admin
    image = models.ImageField(upload_to='media/', default='/no_image.jpg') 
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()

class Task(models.Model):
    title = models.CharField(max_length = 255)
    description = models.TextField()
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    status = models.SmallIntegerField(default = 0) # 0 = Available | 1 = Accepted | 2 = Complete
    image = models.ImageField(upload_to='media/', default='/no_image.jpg')
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    #Relationships 
    uploaded_by = models.ForeignKey(User, related_name = "tasks_uploaded")
    users_bidded = models.ManyToManyField(User, related_name = "tasks")
    accepted_helper = models.ForeignKey(User, related_name = "tasks_helping_with", null=True)

    objects = TaskManager()

class Review(models.Model):
    content = models.TextField()
    rating = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    #Relationships
    user = models.ForeignKey(User, related_name="reviews")
    reviewed_by = models.ForeignKey(User, related_name="reviews_left")

# class Cart(models.Model):
#     created_at = models.DateTimeField(auto_now_add = True)
#     updated_at = models.DateTimeField(auto_now = True)

#     #Relationships
#     user = models.OneToOneField(User)
#     tasks = models.ManyToManyField(Task, related_name = "cart", null=True)