from django.apps import AppConfig


class PizzaApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pizza_api'

    def ready(self):
        import pizza_api.signals  # noqa: F401
