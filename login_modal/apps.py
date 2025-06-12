from django.apps import AppConfig


class LoginModalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login_modal'

    def ready(self):
        import login_modal.signals

