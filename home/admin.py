from django.contrib import admin
from home.models import Login, Tlogs, Tlog_body, Tlog_comment
# Register your models here.

class TlogsAdmin(admin.ModelAdmin):
    list_display=('id', 'title', 'email', 'publish', 'views', 'date')
    search_fields=('title', 'email')
class TlogBodyAdmin(admin.ModelAdmin):
    list_display=('id', 'tlog', 'image', 'email', 'date')
    list_filter=('tlog',)
class TlogCommentAdmin(admin.ModelAdmin):
    list_display=('id', 'tlog', 'comment', 'email', 'date')
    list_filter=('tlog',)
    search_fields=('email',)

admin.site.register(Login)
admin.site.register(Tlogs, TlogsAdmin)
admin.site.register(Tlog_body, TlogBodyAdmin)
admin.site.register(Tlog_comment, TlogCommentAdmin)