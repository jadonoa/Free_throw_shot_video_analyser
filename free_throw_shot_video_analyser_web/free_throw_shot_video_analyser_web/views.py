from django.shortcuts import render
# no need for python code to store as django provides reliable file storage
from django.core.files.storage import FileSystemStorage, default_storage
from .balltracker import createFrames, frames_to_video
from django.conf import settings


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def analysis(request):
    context = {}
    if request.method == "POST":
        uploaded_file = request.FILES['videoFile']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        context['originalURL'] = fs.url(filename)
        path = settings.BASE_DIR + context['originalURL']
        createFrames(path)
        frames_to_video()
        context['trackingVideoURL'] = '/media/trackingVideo.mov'

    return render(request, 'analysis.html', context)
