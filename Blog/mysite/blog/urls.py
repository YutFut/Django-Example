from django.urls import path
from . import views

# определили пространство имен приложения в переменной app_name
app_name = 'blog'

urlpatterns = [
    # post views
    path('post_list/', views.post_list, name='post_list'),
    path('post_list_1/', views.MyPaginator.post_list_1, name='post_list_1'),
    path('post_list_2/', views.MyPaginator.post_list_2, name='post_list_2'),
    path('post_list_3/', views.MyPaginator.post_list_3, name='post_list_3'),
    path('post_list_view/', views.PostListView.as_view(), name='post_list_view'),
    path('<int:year>/<int:month>/<int:day>/<str:author>/<slug:post>/post_detail/',
         views.post_detail, name='post_detail'),
    path('<int:year>/<int:month>/<int:day>/<str:author>/<slug:post>/post_detail_comments/',
         views.post_detail_comments, name='post_detail_comments'),
    path('<int:post_id>/post_share/', views.post_share, name='post_share'),
    path('<int:post_id>/post_comment/', views.post_comment, name='post_comment'),
    path('<int:post_id>/post_comment_1/', views.post_comment_1, name='post_comment_1'),
]
