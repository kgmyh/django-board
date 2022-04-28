# Generated by Django 4.0 on 2022-01-04 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_code', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=200, verbose_name='글 카테고리')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='글제목')),
                ('content', models.TextField(verbose_name='글내용')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='작성일시')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='board.category', verbose_name='글 분류')),
                ('writer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.customuser', verbose_name='작성자')),
            ],
            options={
                'ordering': ['-pk'],
            },
        ),
    ]
