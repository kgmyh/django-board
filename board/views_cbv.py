# Backup of original class-based views

from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Post

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    template_name = 'board/post_create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('board:detail', args=[self.object.pk])

    def form_valid(self,  form):
        form.instance.writer = get_user(self.request)
        return super().form_valid(form)


class PostDetailView(DetailView):
    template_name = "board/post_detail.html"
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(login_required, 'dispatch')
class PostUpdateView(UpdateView):
    template_name = "board/post_update.html"
    form_class = PostForm
    model = Post
    
    def get_success_url(self):
        return reverse_lazy('board:detail', args=[self.object.pk])


@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect("/")


class PostListView(ListView):
    template_name = "board/post_list.html"    
    model = Post
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_group_count = 10
        current_page = int(self.request.GET.get('page', 1))

        if paginator.num_pages == 0:
            context['page_range'] = []
            return context

        start_idx = int((current_page-1)/page_group_count)*page_group_count
        end_idx = start_idx + page_group_count
        page_range = paginator.page_range[start_idx : end_idx]

        start_page = paginator.page(page_range[0])
        end_page = paginator.page(page_range[-1])

        has_previous = start_page.has_previous()
        has_next = end_page.has_next()

        context['page_range'] = page_range
        if has_previous:
            context['has_previous'] = has_previous
            context['previous_page_no'] = start_page.previous_page_number()

        if has_next:
            context['has_next'] = has_next
            context['next_page_no'] = end_page.next_page_number()

        return context

