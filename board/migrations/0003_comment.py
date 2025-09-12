from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('board', '0002_post_up_file_post_up_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='댓글 내용')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='작성일시')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='board.post', verbose_name='게시글')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.customuser', verbose_name='작성자')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]

