from django.shortcuts import render
# no need for python code to store as django provides reliable file storage
from django.core.files.storage import FileSystemStorage
from .balltracker import createFrames, frames_to_video, createBlankFrames
from .makemiss import predict
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
        createBlankFrames(path)
        context['trackingVideoURL'] = '/media/trackingVideo.mov'

        shots_data, make_height_frames, miss_height_frames = predict()

        context['totalShots'] = str(shots_data[0])
        context['madeShots'] = str(shots_data[1])
        context['missedShots'] = str(shots_data[2])
        context['percentage'] = str(shots_data[3]) + '%'

        i = 1
        for frame in make_height_frames:
            context['maxMakeHeight' + str(i)] = '/media/maxHeights/make/' + str(frame)
            i += 1

        i = 1
        for frame in miss_height_frames:
            context['maxMissHeight' + str(i)] = '/media/maxHeights/miss/' + str(frame)
            i += 1

    return render(request, 'analysis.html', context)
