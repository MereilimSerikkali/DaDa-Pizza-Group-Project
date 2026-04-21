from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pizza_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='css_class',
            field=models.CharField(default='ingredient', max_length=50),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='icon',
            field=models.CharField(default='●', max_length=10),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium', max_length=20)),
                ('crust', models.CharField(choices=[('classic', 'Classic'), ('thin', 'Thin'), ('cheese-burst', 'Cheese burst')], default='classic', max_length=20)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ingredients', models.ManyToManyField(blank=True, to='pizza_api.ingredient')),
                ('pizza', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='pizza_api.pizza')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]