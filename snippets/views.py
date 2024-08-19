from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, renderers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import ExtendedUser, Snippet, Audit
from .permissions import IsOwnerOrReadOnly
from .serializers import SnippetSerializer, UserSerializer, AuditSerializer


class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


@api_view(["GET", "POST"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
            "snippets": reverse("snippet-list", request=request, format=format),
        }
    )

@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = ExtendedUser.objects.create_user(username=username, password=password)
    return Response({ "OK": "OK" })

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_user(request):
    username = request.data.get('username')
    user = ExtendedUser.objects.filter(username=username).first()
    user.soft_delete()
    user.save()
    return Response({ "OK": "OK" })        

@api_view(["POST"])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    auth_user = authenticate(username = username, password = password)
    if auth_user:
        e = login(request, auth_user)
        return Response(status=200)
    return Response(status=401)

class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )  

class UserList(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff and self.request.GET.get('show_deleted'):
            return ExtendedUser.objects.all()
        return ExtendedUser.objects.filter(is_deleted=False)            

class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff and self.request.GET.get('show_deleted'):
            return ExtendedUser.objects.all()
        return ExtendedUser.objects.filter(is_deleted=False)  

class AuditList(generics.ListAPIView):
    queryset=Audit.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class = AuditSerializer

class AuditDetail(generics.RetrieveAPIView):
    queryset=Audit.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class = AuditSerializer