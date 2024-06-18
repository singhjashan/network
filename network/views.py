from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json 
from django.contrib import messages


from .models import User, Post, Follow, Like

def edit(request,post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"] 
        edit_post.save()
        return JsonResponse({
            "message":"change successful",
            "data":data["content"]
            })


def un_like(request,post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(post=post, user=user)
    like.delete()
    return JsonResponse({
        "message":"post is unliked!!"
        })


def add_like(request,post_id):
    all_posts = Post.objects.all().order_by("id").reverse()
    
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    new_like = Like(post=post, user=user)
    new_like.save()
    
    likes = Like.objects.filter(post=post)
    like_count = likes.count()
    
    all_likes = Like.objects.all()
    
    #like count
    likedByWhom = {}
    for post in all_posts:
        users_liked_post = User.objects.filter(user_like__post=post)
        likedByWhom[post.id] = {
            'like_count': users_liked_post.count()  
        }
    likedByWhom_json = json.dumps(likedByWhom)
    
    who_liked_you = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked_you.append(like.post.id)
    except:
        who_liked_you = []
    
    return JsonResponse({
        "message":"post is liked!!",
        "like_count": like_count,
        "likedByWhom":likedByWhom_json,
        "who_liked_you": who_liked_you,
        
    })
 

def delete_post(request, post_id):
    if request.method == "DELETE":
        post = Post.objects.get(pk=post_id)
        post.delete()
        return JsonResponse({
            "message": "Post deleted successfully"
            })


def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()
    
    # pegination
    peginator = Paginator(all_posts,10)
    page_no = request.GET.get('page')
    posts_of_the_page = peginator.get_page(page_no)
    
    all_likes = Like.objects.all()
    
    who_liked_you = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked_you.append(like.post.id)
    except:
        who_liked_you = []
        
    # like count 
    likedByWhom = {}
    for post in all_posts:
        users_liked_post = User.objects.filter(user_like__post=post)
        likedByWhom[post.id] = {
            'like_count': users_liked_post.count()  
        }
    likedByWhom_json = json.dumps(likedByWhom)
        
    
    return render(request, "network/index.html", {
        "all_posts": all_posts,
        "posts_of_the_page":posts_of_the_page,
        "who_liked_you": who_liked_you,
        "likedByWhom":likedByWhom_json,
    })
    
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(user=user).order_by("id").reverse()
    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)
    
    try:
        check_follow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(check_follow) != 0:
            is_following = True
        else:
            is_following = False
    except:
        is_following = False
        
    # pegination
    peginator = Paginator(all_posts,10)
    page_no = request.GET.get('page')
    posts_of_the_page = peginator.get_page(page_no)
    
    # who_liked_you
    all_likes = Like.objects.all()
    who_liked_you = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked_you.append(like.post.id)
    except:
        who_liked_you = []
        
        
    # like count 
    likedByWhom = {}
    for post in all_posts:
        users_liked_post = User.objects.filter(user_like__post=post)
        likedByWhom[post.id] = {
            'like_count': users_liked_post.count()  
        }
    likedByWhom_json = json.dumps(likedByWhom)
    
    return render(request, "network/profile.html",{
        "all_posts": all_posts,
        "posts_of_the_page":posts_of_the_page,
        "username": user.username,
        "following": following,
        "followers": followers,
        "is_following": is_following,
        "user_pr": user,
        "who_liked_you": who_liked_you,
        "likedByWhom":likedByWhom_json,       
    })
    
    
def following(request):
    current_user = User.objects.get(pk=request.user.id)
    following_people =Follow.objects.filter(user=current_user)
    all_posts = Post.objects.all().order_by('id').reverse()
    following_posts = []
    for post in all_posts:
        for prsn in following_people:
            if prsn.user_follower == post.user:
                following_posts.append(post)
    # pegination
    peginator = Paginator(following_posts, 10)
    page_no = request.GET.get('page')
    posts_of_the_page = peginator.get_page(page_no)
    
    # who_liked_you
    all_likes = Like.objects.all()
    who_liked_you = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked_you.append(like.post.id)
    except:
        who_liked_you = []
        
        
    # like count 
    likedByWhom = {}
    for post in all_posts:
        users_liked_post = User.objects.filter(user_like__post=post)
        likedByWhom[post.id] = {
            'like_count': users_liked_post.count()  
        }
    likedByWhom_json = json.dumps(likedByWhom)
    return render(request, "network/following.html",{
        "posts_of_the_page":posts_of_the_page,
        "who_liked_you": who_liked_you,
        "likedByWhom":likedByWhom_json,        
    })
    
    
def follow(request):
    userfollow = request.POST['userfollow']
    current_user = User.objects.get(pk=request.user.id)
    user_follow_data = User.objects.get(username=userfollow)
    f = Follow(user=current_user, user_follower=user_follow_data)
    f.save()
    user_id = user_follow_data.id
    messages.success(request, f"You have started following {user_follow_data}")
    return HttpResponseRedirect(reverse(profile,kwargs={"user_id": user_id}))


def unfollow(request):
    userfollow = request.POST['userfollow']
    current_user = User.objects.get(pk=request.user.id)
    user_follow_data = User.objects.get(username=userfollow)
    f = Follow.objects.get(user=current_user, user_follower=user_follow_data)
    f.delete()
    user_id = user_follow_data.id
    messages.success(request, f"You have unfollowed {user_follow_data}")
    return HttpResponseRedirect(reverse(profile, kwargs={"user_id": user_id}))

def new_post(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))
 
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")