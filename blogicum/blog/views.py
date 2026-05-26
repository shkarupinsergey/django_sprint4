from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from blog.models import Post, Category, User, Comment
from .forms import PostForm, ProfileEditForm, CommentForm


class GetPostsMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True, pub_date__lte=now(),
                               category__is_published=True).annotate(
                                   comment_count=Count('comments'))


class PostChangeMixin:
    model = Post
    template_name = 'blog/create.html'

    form_class = PostForm
    context_object_name = 'form'


class CommentChangeMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_pk'])

        if self.request.user != comment.author:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])

        return comment


class PostListView(GetPostsMixin, ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = 'page_obj'

    ordering = '-pub_date'
    paginate_by = 10


class PostDetailView(GetPostsMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['pk'],
        )

        queryset = self.get_queryset()

        if self.request.user != post.author:
            post = get_object_or_404(queryset, pk=self.kwargs['pk'])

        return post

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['comments'] = self.object.comments.order_by('created_at')
        content['form'] = CommentForm()

        return content


class CategoryPostsListView(GetPostsMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'

    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        post_list = super().get_queryset().filter(category=self.category)

        return post_list

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['category'] = self.category

        return content


class ProfileListView(GetPostsMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'

    paginate_by = 10

    def get_queryset(self):
        self.profile = get_object_or_404(
            User, username=self.kwargs['username'])

        posts = Post.objects.select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')
                   ).filter(author=self.profile).order_by('-pub_date')

        if self.request.user != self.profile:
            posts = super().get_object()

        return posts

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['profile'] = self.profile

        return content


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'

    form_class = ProfileEditForm
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, PostChangeMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, PostChangeMixin, UpdateView):
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, PostChangeMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        post = super().get_object()
        if self.request.user != post.author:
            return reverse_lazy(
                'blog:post_detail',
                kwargs={'pk': self.kwargs['pk']}
            )
        return post


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs['pk'], is_published=True)

    def get_context_data(self, **kwargs):
        content = super().get_context_data(**kwargs)
        content['post'] = self.get_post()
        return content

    def form_valid(self, form):
        post = self.get_object()
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class CommentUpdateView(LoginRequiredMixin, CommentChangeMixin, UpdateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.save()
        return redirect('blog:post_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )


class CommentDeleteView(LoginRequiredMixin, CommentChangeMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
        )
