# Generated by Django 4.0 on 2022-04-10 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mettrd', '0004_alter_graph_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='graph',
            name='subname',
            field=models.CharField(blank=True, max_length=83, verbose_name='подзаголовок'),
        ),
        migrations.AddField(
            model_name='graph',
            name='tagsmet',
            field=models.CharField(blank=True, max_length=210, verbose_name='теги (через ,)'),
        ),
        migrations.AlterField(
            model_name='graph',
            name='ID_out',
            field=models.CharField(blank=True, max_length=50, verbose_name='ID_div для вывода'),
        ),
        migrations.AlterField(
            model_name='graph',
            name='file_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Файл данных'),
        ),
        migrations.AlterField(
            model_name='graph',
            name='name',
            field=models.CharField(blank=True, max_length=85, verbose_name='Заголовок метрики'),
        ),
        migrations.AlterField(
            model_name='graph',
            name='variable',
            field=models.CharField(blank=True, max_length=50, verbose_name='Переменная данных'),
        ),
    ]
