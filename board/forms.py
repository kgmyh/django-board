# board/forms.py
from django import forms
from .models import Post

#form 클래스 - forms.Form 상속
#ModelForm 클래스 - forms.ModelForm 상속
class PostForm(forms.ModelForm):
    
    # 내부(Nested/Inner) 클래스로 Meta 클래스를 정의 => ModelForm관련 설정
    class Meta:
        model = Post
        # fields = "__all__" 

        exclude = ['writer'] 