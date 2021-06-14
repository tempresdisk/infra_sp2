from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('title', 'name', 'slug')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'slug')


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'year', 'category')
    search_fields = ('name', 'description', 'year', 'genre', 'category')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'description', 'year', 'category')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'text', 'author')
    search_fields = ('title', 'author')
    empty_value_display = '-пусто-'
    list_filter = ('pub_date', 'title', 'author')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pub_date', 'text', 'author')
    search_fields = ('review', 'author')
    empty_value_display = '-пусто-'
    list_filter = ('pub_date', 'review', 'author')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
