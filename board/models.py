# board/models.py
from django.db import models

from account.models import CustomUser

# Create your models here.
# 글의 카테고리
class Category(models.Model):
    category_code = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=200, verbose_name="글 카테고리")
    
    def __str__(self):
        return f"{self.category_name}"


# 게시물(글)
# title(제목), content(글내용), create_at(등록 일시), update_at(수정일시) + id(자동증가) + , writer(글쓴 사람-후에 추가.)
class Post(models.Model):
    # 글작성자 컬럼 추가. => account.models.CustomUser 참조
    writer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, verbose_name='작성자', null=True, blank=True)

    title = models.CharField(max_length=255, verbose_name="글제목") #NOT NULL, 빈문자열을 허용X
    content = models.TextField(verbose_name='글내용') #TextField: 대용량 text
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name="글 분류", null=True, blank=True)
    #작성일시. auto_now_add=True(기본값:False) => insert 시점의 일시를 저장하고 그 이후에는 update하지 않음.
    create_at = models.DateTimeField(verbose_name='작성일시', auto_now_add=True)
    #수정일시. auto_now=True(기본값:False) -> insert/update 할 때마다 그 시점의 일시를 저장.
    update_at = models.DateTimeField(verbose_name='수정일시', auto_now=True)

    #### 업로드 파일 관련 Field 선언
    # 일반파일 
    up_file = models.FileField(verbose_name='업로드 파일', upload_to="files", # media/files 아래 파일들 저장
                               null=True, blank=True #null값을 가질수 있는 컬럼
                               )
    # 이미지파일-ImageField 사용하려면 Pillow 패키지를 설치.
    up_image = models.ImageField(verbose_name="업로드 이미지", upload_to="images/%Y/%m/%d",
                                 null=True, blank=True)

    def __str__(self):
        return f"{self.pk}. {self.title}"

    class Meta:
        ordering = ["-pk"]