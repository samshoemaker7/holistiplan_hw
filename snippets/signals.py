from django.core.signals import request_finished
from django.dispatch import receiver
from crum import get_current_user

@receiver(request_finished)
def audit_signal_handler(sender, **kwargs):
    model_name = sender.__name__ if sender is not None else "Unknown"

    logged_models = {'ExtendedUser', 'Snippet'}

    if model_name not in logged_models:
        return

    from .models import Audit
    
    instance = kwargs['instance'] if 'instance' in kwargs else None
    created = kwargs['created'] if 'created' in kwargs else False
    user = get_current_user()
    action = "destroy"
    # determine what type of action is currently happening
    if 'created' in kwargs:
        action = "create" if created else "update"
    
    new_audit = Audit(
        action=action, 
        model_name=model_name, 
        user=user,
        object_id=instance.pk if instance != None else None
    )
    new_audit.save()