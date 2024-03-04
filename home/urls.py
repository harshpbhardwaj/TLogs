from django.contrib import admin
from django.urls import path, include
from home import views
from django.conf import settings
from django.conf.urls.static import static 

from home.views import HexaViewSet, BodyViewSet, CommentViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'tlogs', HexaViewSet)
router.register(r'body', BodyViewSet)
router.register(r'comments', CommentViewSet)

# urlpatterns = [
#     path('rest/', include(router.urls))
# ]



urlpatterns = [
    # page links
    path('', views.index, name='home'),
    path('home', views.index, name='home'),
    path('profile', views.profile, name='profile'),
    path('profile/<id>', views.profiles, name='profiles'),
    path('view/<id>/', views.view, name='view'),
    path('signout', views.sign_out, name='sign_out'),
    path("about", views.about, name='about'),
    path("contact", views.contact, name='contact'),

    path('post', views.post, name='post'),
    path('edit_tlog/<id>', views.edit_tlog, name='edit_tlog'),
    path('save_edited_tlog', views.save_edited_tlog, name='save_edited_tlog'),

    # form posts
    path("add_new_comment", views.add_new_comment, name='add_new_comment'),
    
    # ajax links
    path("add_new_tlog", views.add_new_tlog, name='add_new_tlog'),
    path("delete_tlog", views.delete_tlog, name='delete_tlog'),
    path("manage_tlog_privacy", views.manage_tlog_privacy, name='manage_tlog_privacy'),
    path("save_user_fullname", views.save_user_fullname, name='save_user_fullname'),
    path('maildomainverify/<id>', views.maildomainverify, name='maildomainverify'),
    path('reset-password-mail', views.reset_password_mail, name='reset_password_mail'),
    path('reset-password/<id>', views.reset_password, name='reset_password'),
    path('news', views.get_news, name='news'),
    path('list-users', views.list_users, name='list_users'),


    # rest api
    path('rest/', include(router.urls))
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)