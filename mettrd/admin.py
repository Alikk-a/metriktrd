from django.contrib import admin

# Register your models here.
from .models import Post, City, Graph, Page, Tranzact, Cursor
admin.site.register(Post)
admin.site.register(City)
admin.site.register(Graph)
admin.site.register(Page)
admin.site.register(Tranzact)
admin.site.register(Cursor)