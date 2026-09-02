from django import forms
from .models import Post, Comment, Tag


class PostForm(forms.ModelForm):

    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "funny, cats, mondaymood (comma separated)",
                "id": "id_tags_input",
            }
        ),
        help_text="Add up to 5 tags, separated by commas."
    )

    class Meta:
        model = Post
        fields = [
            "category",
            "title",
            "content",
            "image",
        ]

        widgets = {
            "category": forms.Select(
                attrs={"class": "form-select"}
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Give your meme a catchy title...",
                    "maxlength": 200,
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add a caption or description...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        names = [t.strip().lstrip("#") for t in raw.split(",") if t.strip()]
        return names[:5]

    def save(self, commit=True):
        post = super().save(commit=commit)

        tag_names = self.cleaned_data.get("tags", [])

        def sync_tags():
            tag_objs = []
            for name in tag_names:
                existing = Tag.objects.filter(name__iexact=name).first()
                tag = existing or Tag.objects.create(name=name)
                tag_objs.append(tag)
            post.tags.set(tag_objs)

        if commit:
            sync_tags()
        else:
            post.save_tags_m2m = sync_tags

        return post


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["content"]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Write your comment...",
                }
            )
        }
