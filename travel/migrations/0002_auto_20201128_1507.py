# Generated by Django 3.1.2 on 2020-11-28 06:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewmodel',
            name='access_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='access_name', to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
        migrations.AddField(
            model_name='reviewmodel',
            name='user_value_ave',
            field=models.DecimalField(decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AlterField(
            model_name='animemodel',
            name='anime_genre',
            field=models.CharField(choices=[('SF', 'SF'), ('ギャグ', 'ギャグ'), ('恋愛', '恋愛'), ('青春', '青春'), ('ホラー', 'ホラー'), ('日常', '日常'), ('ミステリー', 'ミステリー'), ('バトル', 'バトル')], max_length=15),
        ),
        migrations.AlterField(
            model_name='reviewmodel',
            name='post_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='reviewmodel',
            name='user_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_name', to=settings.AUTH_USER_MODEL, to_field='username'),
        ),
        migrations.CreateModel(
            name='User_Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.TextField()),
                ('count_SF', models.IntegerField(blank=True, default=0, null=True)),
                ('SF_sum_value1', models.IntegerField(blank=True, default=0, null=True)),
                ('count_love', models.IntegerField(blank=True, default=0, null=True)),
                ('user_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
