from decimal import Decimal

from django.contrib.auth import get_user_model

from .models import Category, Ingredient, Pizza

User = get_user_model()


def ensure_demo_data():
    category, _ = Category.objects.get_or_create(name='Signature', defaults={'slug': 'signature'})

    ingredient_defaults = [
        ('Pepperoni', Decimal('1.50'), '●', 'pepperoni'),
        ('Mushrooms', Decimal('1.10'), '◔', 'mushroom'),
        ('Olives', Decimal('0.90'), '◉', 'olive'),
        ('Basil', Decimal('0.80'), '✦', 'basil'),
        ('Mozzarella', Decimal('1.30'), '✹', 'mozzarella'),
        ('Chicken', Decimal('1.70'), '◆', 'chicken'),
        ('Jalapeños', Decimal('1.00'), '✦', 'jalapeno'),
        ('Cherry Tomatoes', Decimal('1.00'), '●', 'tomato'),
    ]
    ingredients = {}
    for name, price, icon, css_class in ingredient_defaults:
        ingredient, created = Ingredient.objects.get_or_create(
            name=name,
            defaults={
                'extra_price': price,
                'icon': icon,
                'css_class': css_class,
            },
        )
        if not created:
            updated_fields = []
            if not ingredient.extra_price:
                ingredient.extra_price = price
                updated_fields.append('extra_price')
            if not ingredient.icon:
                ingredient.icon = icon
                updated_fields.append('icon')
            if not ingredient.css_class:
                ingredient.css_class = css_class
                updated_fields.append('css_class')
            if updated_fields:
                ingredient.save(update_fields=updated_fields)
        ingredients[name] = ingredient

    pizza_defaults = [
        {
            'name': 'Royal Pepperoni',
            'description': 'Spicy pepperoni, mozzarella and tomato sauce.',
            'image_emoji': '🍕',
            'price': Decimal('12.90'),
            'ingredient_names': ['Pepperoni', 'Mozzarella'],
        },
        {
            'name': 'Forest Mushroom',
            'description': 'Creamy mushroom pizza with basil and mozzarella.',
            'image_emoji': '🍄',
            'price': Decimal('11.40'),
            'ingredient_names': ['Mushrooms', 'Basil', 'Mozzarella'],
        },
        {
            'name': 'Chicken Heat',
            'description': 'Chicken, jalapeños, tomatoes and rich cheese.',
            'image_emoji': '🌶️',
            'price': Decimal('13.80'),
            'ingredient_names': ['Chicken', 'Jalapeños', 'Cherry Tomatoes', 'Mozzarella'],
        },
    ]

    for payload in pizza_defaults:
        pizza, created = Pizza.objects.get_or_create(
            name=payload['name'],
            defaults={
                'description': payload['description'],
                'image_emoji': payload['image_emoji'],
                'price': payload['price'],
                'category': category,
                'is_active': True,
            },
        )
        if created:
            pizza.ingredients.set([ingredients[name] for name in payload['ingredient_names']])
        else:
            if pizza.category_id is None:
                pizza.category = category
                pizza.save(update_fields=['category'])
            if not pizza.ingredients.exists():
                pizza.ingredients.set([ingredients[name] for name in payload['ingredient_names']])

    seeded_users = [
        {
            'username': 'demo@pizzeria.com',
            'email': 'demo@pizzeria.com',
            'password': 'pizza123',
            'first_name': 'DaDa',
            'last_name': 'Lover',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'customer@pizzeria.com',
            'email': 'customer@pizzeria.com',
            'password': 'customer123',
            'first_name': 'Regular',
            'last_name': 'Customer',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'admin@pizzeria.com',
            'email': 'admin@pizzeria.com',
            'password': 'admin123',
            'first_name': 'Pizza',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True,
        },
    ]

    for payload in seeded_users:
        user, created = User.objects.get_or_create(
            username=payload['username'],
            defaults={
                'email': payload['email'],
                'first_name': payload['first_name'],
                'last_name': payload['last_name'],
                'is_staff': payload['is_staff'],
                'is_superuser': payload['is_superuser'],
            },
        )
        changed = []
        for field in ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser'):
            value = payload[field]
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed.append(field)
        if created or not user.check_password(payload['password']):
            user.set_password(payload['password'])
            changed.append('password')
        if changed:
            user.save()
