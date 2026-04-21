from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .seed import ensure_demo_data


@receiver(post_migrate)
def seed_pizza_demo_data(sender, **kwargs):
    if getattr(sender, 'name', None) == 'pizza_api':
        ensure_demo_data()
