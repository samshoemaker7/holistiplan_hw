from django.contrib import admin
from .models import Snippet, ExtendedUser, Audit


class SnippetAdmin(admin.ModelAdmin):
    readonly_fields = ("highlighted",)

admin.site.register(Snippet, SnippetAdmin)
admin.site.register(ExtendedUser)
admin.site.register(Audit)