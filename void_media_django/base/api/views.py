from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Posts
from .serializer import PostsSerializer
from django.http import HttpResponse

@api_view(['GEt'])
def getRoutes(request):

    routes = [
        'GET /api',
        'GET /api/profile',
        'GET /api/profile/:id',
    ]
    return Response(routes)

@api_view(['GET'])
def getPosts(request):
    posts = Posts.objects.all()
    serializer = PostsSerializer(posts , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getPost(request, pk):
    post = Posts.objects.get(id=pk)
    serializer = PostsSerializer(post , many=False)
    return Response(serializer.data)
