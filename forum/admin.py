from django.contrib import admin
from .models import *

admin.site.register(Post)
admin.site.register(Replies)
admin.site.register(Section)
admin.site.register(SectionTheme)

# Register your models here.
