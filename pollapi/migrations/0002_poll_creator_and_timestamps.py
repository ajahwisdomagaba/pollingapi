import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pollapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='creator',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='polls',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='poll',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='option',
            name='poll',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='options',
                to='pollapi.poll',
            ),
        ),
        migrations.AlterField(
            model_name='vote',
            name='option',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='vote_records',
                to='pollapi.option',
            ),
        ),
        migrations.AlterField(
            model_name='vote',
            name='poll',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='votes',
                to='pollapi.poll',
            ),
        ),
        migrations.AlterField(
            model_name='vote',
            name='voter',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='votes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
