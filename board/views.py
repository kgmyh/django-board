# board/views.py

from django.shortcuts import redirect, get_object_or_404, render

from .forms import PostForm, CommentForm
from .models import Post, Comment

########################################
# 로그인 처리
########################################
from django.contrib.auth.decorators import login_required #로그인여부를 확인해서 로그인 안한경우 settings.py의 LOGIN_URL의 경로로 이동.
from django.contrib.auth import get_user  # 로그인한 사용자의 User Model객체를 반환.
from django.core.paginator import Paginator


# 글등록
# CreateView 등록(저장-insert 처리)
#    get 방식 요청: 입력양식 화면으로 이동(render())
#    post방식 요청: 입력(등록) 처리. 
#                  처리성공: 성공페이지로 이동(redirect) 
#                  처리실패: 입력양식 화면으로 이동(render())
#  class변수
#    - template_name: 입력폼을 작성한 template의 경로
#    - form_class: 입력폼에서 사용할 Form/ModelForm
#    - success_url: 등록 성공후 요청할 View의 url -> redirect방식으로 이동한다. (path parameter로 update한 Model정보를 사용할 경우 get_success_url() 를 오버라이딩.)

# 로그인 한 사용자만 호출할 수 있는 기능.
# 글 작성자를 추가.
#  writer => 글을 작성한(로그인한) 사용자의 CustomUser객체를 사용.
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.writer = request.user
            post.save()
            return redirect('board:detail', post.pk)
    else:
        form = PostForm()
    return render(request, 'board/post_create.html', {'form': form})


# 하나의 글 정보 조회 (pk)
# DetailView - pk로 조회한 결과를 template으로 보내주는 generic View
#    url 패턴: pk를 path 파라미터로 받는다. <type:pk> 변수명을 pk로 지정해야 한다. 
#              이 path parameter값을 이용해 select.
# 속성
#   - template_name: 응답할 template의 경로.
#   - model: PK로 조회할 모델클래스
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('writer').all()
    context = {
        'object': post,
        'comments': comments,
        'comment_form': CommentForm(),
    }
    return render(request, 'board/post_detail.html', context)


# 글 수정처리 
#  UpdateView 
#   - GET 요청처리: pk로 수정할 정보를 조회해서 template(수정 form)으로 전달(render())
#   - POST요청처리: update 처리. redirect방식으로 View를 요청
#  속성
#   - template_name: 수정 form template파일의 경로
#   - form_class: Form/ModelForm 클래스 등록
#   - model : Model 클래스 등록 (수정폼 template에 전달할 값을 조회하기 위해)
#   - success_url: 수정 처리후 redirect 방식으로 이동할 View의 url (path parameter로 update한 Model정보를 사용할 경우 get_success_url() 를 오버라이딩.)
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.writer != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('board:detail', post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'board/post_update.html', {'form': form})


# 삭제처리
#  generice View: DeleteView를 사용=>삭제 확인 화면을 거쳐서 삭제 처리한다.
# 함수기반으로 작성. path parameter로 삭제할 글의 id(pk)를 받아서 삭제처리.

# 로그인 한 사용자만 호출 가능
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.writer != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    post.delete()
    return redirect("/") 

# 글 목록
# ListView 구현 - 지정한 Model의 전체 데이터를 조회하여 Template으로 전달한다.
# 속성
#  - template_name : 결과를 보여줄 template의 경로
#  - model : 조회할 모델클래스를 지정
#  조회결과를 template에 "object_list" 또는 "모델이름소문자_list(post_list)" 라는 이름으로 전달.
#  ListView는 paging기능 지원

# 페이징 처리 적용 ListView
def post_list(request):
    qs = Post.objects.all()
    paginator = Paginator(qs, 10)
    page_no = request.GET.get('page', '1')
    page_obj = paginator.get_page(page_no)

    context = {
        'object_list': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': paginator.num_pages > 1,
    }

    page_group_count = 10
    current_page = int(page_no or 1)
    if paginator.num_pages:
        start_idx = int((current_page-1)/page_group_count)*page_group_count
        end_idx = start_idx + page_group_count
        page_range = list(paginator.page_range)[start_idx:end_idx]
        context['page_range'] = page_range
        start_page = paginator.page(page_range[0])
        end_page = paginator.page(page_range[-1])
        if start_page.has_previous():
            context['has_previous'] = True
            context['previous_page_no'] = start_page.previous_page_number()
        if end_page.has_next():
            context['has_next'] = True
            context['next_page_no'] = end_page.next_page_number()
    else:
        context['page_range'] = []

    return render(request, 'board/post_list.html', context)





########################################
# 댓글 AJAX View들
########################################
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string


@login_required
@require_POST
def comment_create(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'error': '내용을 입력하세요.'}, status=400)
    comment = Comment.objects.create(
        post=post,
        writer=get_user(request),
        content=form.cleaned_data['content']
    )
    html = render_to_string('board/_comment_item.html', {'comment': comment, 'user': request.user}, request=request)
    return JsonResponse({'ok': True, 'html': html, 'id': comment.pk})


@login_required
@require_POST
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.writer != request.user:
        return HttpResponseForbidden()
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'error': '내용을 입력하세요.'}, status=400)
    comment.content = form.cleaned_data['content']
    comment.save(update_fields=['content', 'update_at'])
    html = render_to_string('board/_comment_item.html', {'comment': comment, 'user': request.user}, request=request)
    return JsonResponse({'ok': True, 'html': html, 'id': comment.pk})


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.writer != request.user:
        return HttpResponseForbidden()
    comment.delete()
    return JsonResponse({'ok': True})
