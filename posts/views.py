from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from .models import Post, Author, PostView, Category
from .forms import CommentForm, PostForm, CategoryForm
from marketing.models import SignUp
from django.views.generic import CreateView, ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }

    return render(request, 'search_results.html', context)


def get_category_count():
    queryset = Post.objects.values('categories__title').annotate(Count('categories'))
    return queryset


def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method == "POST":
        email = request.POST["email"]
        new_signup = SignUp()
        new_signup.email = email
        new_signup.save()

    context = {
        'object_list': featured,
        'latest': latest,
    }
    return render(request, 'index.html', context)


def blog(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.order_by('-timestamp')
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)

    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        # go to first page if page if not an integer
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        # returns the actual number of pages ina query set. If empty page, return last page.
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,
    }
    return render(request, 'blog.html', context)


def post(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post_detail", kwargs={
                'id': post.pk
            }))
    context = {
        'form': form,
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count,
    }
    return render(request, 'post.html', context)


@staff_member_required
def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save(commit=False)
            form.instance.author = author
            form.save()
            return redirect(reverse("post_detail", kwargs=
            {'id': form.instance.id}))
    else:
        form = PostForm()
    context = {
        'form': form,
        'title': title
    }
    return render(request, "post_create.html", context)


@staff_member_required
def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post_detail", kwargs=
            {'id': form.instance.id}))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


@staff_member_required
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post_list"))


@method_decorator(staff_member_required, name='dispatch')
class CategoryCreate(CreateView, SuccessMessageMixin):
    template_name = 'category_create.html'
    form_class = CategoryForm
    success_url = reverse_lazy('category_create')

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Category.objects.all()
        return super(CategoryCreate, self).get_context_data(**kwargs)


@staff_member_required
def delete_category(request, title):
    category = Category.objects.get(title=title)
    category.delete()
    return redirect('category_create')
