from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, renderers, viewsets, status
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

class UserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        is_staff = self.request.user.is_staff
        show_deleted = self.request.GET.get('show_deleted')
        
        queryset = ExtendedUser.objects.filter(is_deleted=False)
        if is_staff and show_deleted:
            queryset = ExtendedUser.objects.all()

        return queryset
    
    # Get a list of all users
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response({
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        })
    
    # Create a new user
    def post(self, request):
        is_staff = request.user.is_staff
        if not is_staff:
            return Response(
                {
                    "message": "Authentication credentials were not provided."
                },
                status = status.HTTP_401_UNAUTHORIZED
            )
        
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {
                    "message": "Missing username and/or password."
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        user = ExtendedUser.objects.create_user(username=username, password=password)
        return Response(
            { 
                "message": "New user was created."
            },
            status=status.HTTP_201_CREATED
        )

class UserDetail(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        is_staff = self.request.user.is_staff
        show_deleted = self.request.GET.get('show_deleted')
        if is_staff and show_deleted:
            return ExtendedUser.objects.all()
        return ExtendedUser.objects.filter(is_deleted=False)

    # Soft delete a user
    def delete(self, request, *args, **kwargs):
        is_staff = request.user.is_staff
        if not is_staff:
            return Response(
                {
                    "message": "Authentication credentials were not provided."
                },
                status = status.HTTP_401_UNAUTHORIZED
            )
        
        primary_key = kwargs['pk']
        user = ExtendedUser.objects.filter(pk=primary_key).first()
        user.soft_delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AuditList(generics.ListAPIView):
    queryset=Audit.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class = AuditSerializer

class AuditDetail(generics.RetrieveAPIView):
    queryset=Audit.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class = AuditSerializer