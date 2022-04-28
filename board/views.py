# board/views.py

from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Post

########################################
# 로그인 처리
########################################
from django.contrib.auth.decorators import login_required #로그인여부를 확인해서 로그인 안한경우 settings.py의 LOGIN_URL의 경로로 이동.
from django.utils.decorators import method_decorator # class의 메소드에 decorator를 선언해 주는 decorator
from django.contrib.auth import get_user  # 로그인한 사용자의 User Model객체를 반환.


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
@method_decorator(login_required, name='dispatch')  #dispatch()메소드에 @login_required 장식자를 적용.
class PostCreateView(CreateView):
    template_name = 'board/post_create.html'
    form_class = PostForm
    # success_url = reverse_lazy("board:detail")    #등록 처리후 이동할 경로->redirect방식이동=>view의 url을 등록 

    # success_url 설정을 대신
    #   success_url에서 insert한 Model객체를 접근하려면 이 메소드를 overriding 해야 한다.
    #   insert한 모델객체 조회: self.objects
    def get_success_url(self):
        # 반환값: 등록 성공후 redirect 방식으로 이동할 View의 url을 문자열로 반환.
        return reverse_lazy('board:detail', args=[self.object.pk]) # args: path parameter로 전달할 값들을 리스트에 순서대로 담는다.

    ##################################
    # form_valid(): CreateView, UpdateView에서 Post 요청 처리시 insert/delete 하기 전/후로 해야 하는 작업이 있을 경우 form_valid()를 오버라이딩 한다.
    # 
    # 로그인한 사용자의 User 모델객체를 insert하기 전에 model에 넣어준다.
    # 매개변수: form - (검증을 통과한) ModelForm을 첫번째 매개변수로 받는다.
    def form_valid(self,  form):
        
        post = form.save(commit=False)  #ModelForm.save() : Model 객체가 반환
        post.writer = get_user(self.request)  #로그인한 User객체
        # post.save() 최종 update & commit => super에서 처리.
        return super().form_valid(form)


# 하나의 글 정보 조회 (pk)
# DetailView - pk로 조회한 결과를 template으로 보내주는 generic View
#    url 패턴: pk를 path 파라미터로 받는다. <type:pk> 변수명을 pk로 지정해야 한다. 
#              이 path parameter값을 이용해 select.
# 속성
#   - template_name: 응답할 template의 경로.
#   - model: PK로 조회할 모델클래스
class PostDetailView(DetailView):
    template_name = "board/post_detail.html"
    model = Post 
    # pk로 조회할 Model 클래스. 조회결과를 "post"(모델클래스명을 소문자), "object" 라는 이름으로 template에게 전달.


# 글 수정처리 
#  UpdateView 
#   - GET 요청처리: pk로 수정할 정보를 조회해서 template(수정 form)으로 전달(render())
#   - POST요청처리: update 처리. redirect방식으로 View를 요청
#  속성
#   - template_name: 수정 form template파일의 경로
#   - form_class: Form/ModelForm 클래스 등록
#   - model : Model 클래스 등록 (수정폼 template에 전달할 값을 조회하기 위해)
#   - success_url: 수정 처리후 redirect 방식으로 이동할 View의 url (path parameter로 update한 Model정보를 사용할 경우 get_success_url() 를 오버라이딩.)
@method_decorator(login_required, 'dispatch')
class PostUpdateView(UpdateView):
    template_name = "board/post_update.html"
    form_class = PostForm
    model = Post
    
    def get_success_url(self):
        return reverse_lazy('board:detail', args=[self.object.pk])


# 삭제처리
#  generice View: DeleteView를 사용=>삭제 확인 화면을 거쳐서 삭제 처리한다.
# 함수기반으로 작성. path parameter로 삭제할 글의 id(pk)를 받아서 삭제처리.

# 로그인 한 사용자만 호출 가능
@login_required
def post_delete(request, pk):
    
    post = Post.objects.get(pk=pk) 
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
class PostListView(ListView):
    template_name = "board/post_list.html"    
    model = Post
   
    # 페이징 처리 
    #  class변수: paginate_by = 한페이지의 데이터 개수
    #  요청시 url : url?page=번호   http://127.0.0.1:8000/board/list?page=2   page를 생략하면 1번페이지를 조회.
    #  페이지 번호를 template에서 출력하기 위한 값들을 만들어서 template에 전달. => get_context_data()를 오버라이딩
    paginate_by = 10  #한페이지에 10개씩 

    # context data: view가 template에게 전달하는 값(dictionary). key-value쌍.  key: context name, value: context value
    # get_context_data(): Generic View를 구현할 때 template에게 추가적으로 전달해야하는 context data가 있을때 오버라이딩.
    # 페이징관련 값들을 context data에 추가
    #  - 이전/다음 페이지 그룹 유무(그룹의 시작/끝페이지)
    #  - 이전/다음 페이지 번호(그룹의 시작/끝페이지)
    #  - 현재 페이지 속한 페이지 그룹의 페이지 범위(시작 ~ 끝 페이지번호)
    def get_context_data(self, **kwargs):
        # 부모객체의 get_context_data()를 호출해서 generic view가 자동으로 생성한 Context data를 받아온다.
        context = super().get_context_data(**kwargs)
        # ListView에서 paginate_by 속성을 설정하면 context data에 Paginator객체가 등록된다.
        paginator = context['paginator']
        page_group_count = 10 #페이지그룹에 속한 페이지 개수
        current_page = int(self.request.GET.get('page', 1))
        # CBV에서 HttpRequest는 self.request로 사용할 수 있다.

        # 페이지 그룹의 페이지 범위 조회
        start_idx = int((current_page-1)/page_group_count)*page_group_count
        end_idx = start_idx + page_group_count
        page_range = paginator.page_range[start_idx : end_idx]

        # 그룹의 시작 페이지가 이전페이지가 있는지, 그룹의 마지막 페이지가 다음페이지가 있는지 여부 + 페이지 번호
        start_page = paginator.page(page_range[0]) #시작 페이지의 Page객체
        end_page = paginator.page(page_range[-1]) # 마지막 페이지의 Page객체

        has_previous = start_page.has_previous() #시작의 이전페이지가 있는지 여부
        has_next = end_page.has_next() # 마지막 페이지의 다음 페이지가 있는지 여부

        context['page_range'] = page_range
        if has_previous:
            context['has_previous'] = has_previous
            context['previous_page_no'] = start_page.previous_page_number  #시작페이지의 이전 페이지 번호

        if has_next:
            context['has_next'] = has_next
            context['next_page_no'] = end_page.next_page_number #마지막 페이지의 다음 페이지 번호

        return context





