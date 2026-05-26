from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'blog'

posts_url = [
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path(
        '<int:pk>/edit_comment/<int:comment_pk>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment',
    ),
    path(
        '<int:pk>/delete_comment/<int:comment_pk>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment',
    ),
]

profile_url = [
    path('edit/', views.ProfileEditView.as_view(), name='edit_profile'),
    path('<str:username>/', views.ProfileListView.as_view(), name='profile'),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/', include(posts_url)),
    path('category/<slug:category_slug>/',
         views.CategoryPostsListView.as_view(), name='category_posts'),
    path('profile/', include(profile_url)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
