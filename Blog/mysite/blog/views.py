from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Count

from .models import Post, User, Comment
from .forms import EmailPostForm, CommentForm1, CommentForm

from taggit.models import Tag


def post_share(request, post_id):
    # Получение статьи по идентификатору.
    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
        # Форма была отправлена на сохранение.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию.
            cd = form.cleaned_data
            # Отправка электронной почты.
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
            return redirect(reverse('blog:post_detail', args=[
                post.publish.year,
                post.publish.month,
                post.publish.day,
                post.author,
                post.slug
            ]))
    else:
        form = EmailPostForm()
        context = {'post': post, 'form': form}
        return render(request, 'post/post_share.html', context)


# example of using forms.Form
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
        form = CommentForm1(request.POST or None)
        if form.is_valid():
            comment = Comment.objects.create(
                post=post,
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                body=form.cleaned_data['body'],
            )
            comment.save()
            return redirect('/blog/post_list/')
    else:
        form = CommentForm()
        context = {'form': form}
        return render(request, 'post/post_comments.html', context)


# example of using forms.ModelForm
def post_comment_1(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('/blog/post_list/')
    else:
        form = CommentForm()
        context = {'form': form}
        return render(request, 'post/post_comments.html', context)


def post_list(request):
    # запрашиваем из базы данных все опубликованные статьи
    # с помощью менеджера published
    posts = Post.published.all()
    context = {'posts': posts}
    return render(request, 'post/post_list.html', context)


def post_list_tag(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)  # По 3 статьи на каждой странице.
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # Если указанная страница не является целым числом.
        page = paginator.page(1)
    except EmptyPage:
        # Если указанный номер больше, чем всего страниц, возвращаем последнюю.
        page = paginator.page(paginator.num_pages)
    context = {'page': page, 'tag': tag}
    return render(request, 'post/post_list_tag.html', context)


# add pagination
class MyPaginator:
    # rename request in self
    # simple example of pagination
    def post_list_1(self):
        object_list = Post.published.all()
        paginator = Paginator(object_list, 3)
        # Из URL извлекаем номер запрошенной страницы - это значение параметра page
        page_number = self.GET.get('page')
        # Получаем набор записей для страницы с запрошенным номером
        page = paginator.get_page(page_number)
        # page = paginator.page(page_number) there is a function page
        context = {'page': page}
        return render(self, 'post/post_list_1.html', context)

    # add exceptions
    def post_list_2(self):
        object_list = Post.published.all()
        paginator = Paginator(object_list, 3)  # По 3 статьи на каждой странице.
        page = self.GET.get('page')
        try:
            posts = paginator.get_page(page)
        except PageNotAnInteger:
            # Если страница не является целым числом, возвращаем первую страницу.
            posts = paginator.page(1)
        except EmptyPage:
            # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
            posts = paginator.page(paginator.num_pages)
        context = {'page': page, 'posts': posts}
        return render(self, 'post/post_list_2.html', context)

    # combination post_list_1 and post_list_2
    def post_list_3(self):
        object_list = Post.published.all()
        paginator = Paginator(object_list, 3)
        page_number = self.GET.get('page')
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        context = {'page': page}
        return render(self, 'post/post_list_1.html', context)


# PostListView является аналогом функции post_list
class PostListView(ListView):
    queryset = Post.published.all()  # model = Post
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'post/post_list_view.html'


def post_detail(request, year, month, day, author, post):
    post = get_object_or_404(
        Post,
        slug=post,
        author=get_object_or_404(User, username=author),
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    context = {'post': post}
    return render(request, 'post/post_detail.html', context)


def post_detail_comments(request, year, month, day, author, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    # Список активных комментариев для этой статьи.
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # Пользователь отправил комментарий.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий, но пока не сохраняем в базе данных.
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье.
            new_comment.post = post
            # Сохраняем комментарий в базе данных.
            new_comment.save()
            # return redirect(f'/blog/{post.publish.year}/'
            #                 f'{post.publish.month}/'
            #                 f'{post.publish.day}/'
            #                 f'{post.author}/'
            #                 f'{post.slug}/post_detail_comments/')
            return redirect(reverse('blog:post_detail_comments', args=[
                post.publish.year,
                post.publish.month,
                post.publish.day,
                post.author,
                post.slug
            ]))
    else:
        comment_form = CommentForm()
        context = {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form}
        return render(request, 'post/post_detail_comments.html', context)


def post_detail_similar_posts(request, year, month, day, author, post):
    post = get_object_or_404(
        Post,
        slug=post,
        author=get_object_or_404(User, username=author),
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    # Формирование списка похожих статей.
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags', '-publish')[:4]
    context = {'post': post, 'similar_posts': similar_posts}
    return render(request, 'post/post_detail_similar_posts.html', context)
