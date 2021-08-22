from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.urls import reverse

from .models import Post, User
from .forms import EmailPostForm


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
            return redirect('/blog/post_list/')
            # return redirect(reverse('post_detail', args=[
            #     post.publish.year,
            #     post.publish.month,
            #     post.publish.day,
            #     post.author,
            #     post.slug
            # ]))
    else:
        form = EmailPostForm()
        return render(request, 'post/post_share.html', {'post': post, 'form': form})


def post_list(request):
    # запрашиваем из базы данных все опубликованные статьи
    # с помощью менеджера published
    posts = Post.published.all()
    context = {'posts': posts}
    return render(request, 'post/post_list.html', context)


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
