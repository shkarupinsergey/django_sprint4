from django import forms

from .models import Post, Comment, User


class PostForm(forms.ModelForm):
    """Форма для создания поста"""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментария"""

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
