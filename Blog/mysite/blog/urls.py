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
    path('<int:year>/<int:month>/<int:day>/<str:author>/<slug:post>/', views.post_detail, name='post_detail'),
]