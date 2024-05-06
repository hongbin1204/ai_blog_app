from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pytube import YouTube
import assemblyai as aai
from .models import BlogPost
import json
import os

# Create your views here.
@login_required
def index(request):
    return render(request, "index.html")

@csrf_exempt
def generate_blog(request):
    if request.method == "POST":
        link = json.loads(request.body.decode('utf-8'))['youtubelink']
        list = yt_download(link)
        title = list[0]
        content = list[1]
        newentry = BlogPost.objects.create(user=request.user, link=link, title=title, content=content)
        newentry.save()
        return JsonResponse({"content": content})
    return JsonResponse({"content": ""})


def yt_download(link):
    yt = YouTube(link)
    title = yt.title
    stream = yt.streams.filter(only_audio=True).first()
    path = stream.download(output_path='media')
    content = transcription(path)
    return [title, content]

def transcription(path):
    aai.settings.api_key = "a1741dc5b90f4677b5a6b1bd3721e87f"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(path)
    os.remove(path)
    return transcript.text

def blog_list(request):
    blogs = BlogPost.objects.filter(user=request.user)
    return render(request, 'blogs.html', {"blogs": blogs})

def blog_details(request, pk):
    blog = BlogPost.objects.filter(pk=pk).first()
    if request.user == blog.user:
        return render(request, 'blogdetail.html', {"blog": blog})
    else:
        return render(request, 'blogdetail.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse("index"))
        else:
            return render(request, "login.html", {"error_message": "Please double check credentials!"})

    return render(request, "login.html")

def user_signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email =  request.POST['email']
        password = request.POST['password']
        confirmpass = request.POST['repassword']

        if not username or not email or not password or not confirmpass:
            return render(request, "signup.html", {"error_message": "Missing Entry!"})
        elif confirmpass != password:
            return render(request, "signup.html", {"error_message": "Please confirm your password!"})
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except:
            return render(request, "signup.html", {"error_message": "Username is taken!"})
        return redirect(reverse("login"))
    
    return render(request, "signup.html")

def user_logout(request):
    logout(request)
    return redirect(reverse("login"))