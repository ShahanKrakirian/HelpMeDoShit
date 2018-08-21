from django.conf.urls import url
from . import views

urlpatterns = [
    #Login/Reg 
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^login/process$', views.login),
    url(r'^logout$', views.logout),

    #Admin Login/Portal
    url(r'^admin$', views.admin),
    # url(r'^admin/login$', views.admin_login),

    #User Pages 
    url(r'^home$', views.home),
    url(r'^user/(?P<user_id>\w+)$', views.user_profile),
    url(r'^user/(?P<user_id>\w+)/edit$', views.edit_user),
    url(r'^user/(?P<user_id>\w+)/edit/process$', views.edit_user_process),


    #Tasks
    url(r'^task/add$', views.add_task),
    url(r'^task/add/process$', views.add_task_process),
    url(r'^task/(?P<task_id>\d+)$', views.view_task),
    url(r'^task/edit/process/(?P<task_id>\w+)$', views.edit_task_process),
    url(r'^task/delete/(?P<task_id>\d+)$', views.delete_task),
    url(r'^task/edit/(?P<task_id>\d+)$', views.edit_task),
    url(r'^task/(?P<task_id>\d+)/bid$', views.bid_task),
    url(r'^task/(?P<task_id>\d+)/cancel-work-agreement$', views.cancel_work_agreement),
    url(r'^task/(?P<task_id>\d+)/remove-bid$', views.remove_bid),
    url(r'^accept_offer/(?P<task_id>\d+)/(?P<offering_id>\d+)$', views.accept_offer),
    url(r'^decline_offer/(?P<task_id>\d+)/(?P<offering_id>\d+)$', views.decline_offer),
]
