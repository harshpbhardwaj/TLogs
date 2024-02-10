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


    # form posts
    path("add_new_comment", views.add_new_comment, name='add_new_comment'),
    
    # ajax links
    path("add_new_tlog", views.add_new_tlog, name='add_new_tlog'),
    path("delete_tlog", views.delete_tlog, name='delete_tlog'),

    # rest api
    path('rest/', include(router.urls))
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)