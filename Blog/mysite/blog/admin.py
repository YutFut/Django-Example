from django.contrib import admin
from .models import Post, Comment


# @admin.register(Post) выполняет те же действия,
# что и функция admin.site.register():
# регистрирует декорируемый класс – наследник ModelAdmin.
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


# @admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
