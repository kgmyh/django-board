# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# UserAdmin : 관리자앱에서 사용자 관리 화면 => customizing
class CustomUserAdmin(UserAdmin):
    # 기본정보 카테고리 설정
    UserAdmin.fieldsets[1][1]['fields'] = ('name', 'email', 'gender')

    list_display = ['username', 'name', 'email'] #목록


admin.site.register(CustomUser, CustomUserAdmin)