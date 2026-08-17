from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post

        exclude = ( "author","created_at","updated_at",)

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}
                                     ),
            "category": forms.Select(attrs={"class": "form-select"}),

            "content": forms.Textarea(
            attrs={
                "class": "form-control",}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["content",]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write your comment..."
                }
            )
        }