from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model # settings.py 에 등록된 AUTH_USER_MODEL 클래스를 반환.
from django import forms
# CustomUser와 연동된 ModelForm
class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password 확인', widget=forms.PasswordInput())
    
    class Meta:
        # model = CustomUser
        model = get_user_model()
        fields = ["username", "password1",'password2'  ,"name", "email", "gender"]
        # fields = '__all__'
        # model의 Field들의 widget(입력양식)을 변경하고자 할때 widgets 속성에 딕셔너리에 등록한다. (field명:widget객체)
        # widgets = {
        #     "name":forms.Textarea
        # }

