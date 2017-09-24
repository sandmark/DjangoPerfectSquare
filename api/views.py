"""
api/views.py
"""
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from cms.models import Content
from api.serializers import ContentSerializer


@csrf_exempt
def content_list(request):
    """
    List all contents, or create a new content.
    """
    if request.method == 'GET':
        contents = Content.objects.all()
        serializer = ContentSerializer(contents, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ContentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def content_detail(request, pk):
    """
    Retrieve, update or delete a content.
    """
    try:
        content = Content.objects.get(pk=pk)
    except Content.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = ContentSerializer(content)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ContentSerializer(content, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        content.delete()
        return HttpResponse(status=204)
