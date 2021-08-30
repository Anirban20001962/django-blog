from .models import Post
from django.views.generic import ListView
from django.urls import reverse
from .froms import CommentForm
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.


class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        querysert = super().get_queryset()
        data = querysert[:3]
        return data


class AllPostPageView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    context_object_name = "posts"


class PostDetailView(View):
    def is_stored_post(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        is_saved_for_later = False
        if stored_posts is None:
            is_saved_for_later = False
        elif post_id in stored_posts:
            is_saved_for_later = True
        return is_saved_for_later

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        is_saved_for_later = self.is_stored_post(request, post.id)
        return render(
            request,
            "blog/post-detail.html",
            {
                "post": post,
                "post_tags": post.tags.all(),
                "comment_form": CommentForm(),
                "comments": post.comments.all().order_by("-id"),
                "saved_for_later": is_saved_for_later,
            },
        )

    def post(self, request, slug):
        commet_form = CommentForm(request.POST)
        post = get_object_or_404(Post, slug=slug)
        is_saved_for_later = self.is_stored_post(request, post.id)
        if commet_form.is_valid():
            comment = commet_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(reverse("post-detail-page", args=[slug]))

        return render(
            request,
            "blog/post-detail.html",
            {
                "post": post,
                "post_tags": post.tags.all(),
                "comment_form": commet_form,
                "comments": post.comments.all().order_by("-id"),
                "saved_for_later": is_saved_for_later,
            },
        )


class ReadLaterView(View):
    def post(self, request):
        stored_posts = request.session.get("stored_posts")

        if stored_posts is None:
            stored_posts = []

        post_id = int(request.POST["post_id"])

        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)

        request.session["stored_posts"] = stored_posts

        return redirect("starting_page")

    def get(self, request):
        stored_posts = request.session.get("stored_posts")

        context = {}

        if stored_posts is None or len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False

        else:
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True

        return render(request, "blog/stored-post.html", context)
