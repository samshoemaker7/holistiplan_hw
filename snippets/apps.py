from django.apps import AppConfig
from django.db.models.signals import pre_delete, post_save

class SnippetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "snippets"
    
    def ready(self):
        from .signals import audit_signal_handler
        post_save.connect(audit_signal_handler)
        pre_delete.connect(audit_signal_handler)