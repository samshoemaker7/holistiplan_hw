from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from snippets import views

urlpatterns = [
    path("snippets/", views.SnippetList.as_view(), name="snippet-list"),
    path("snippets/<int:pk>/", views.SnippetDetail.as_view(), name="snippet-detail"),
    path(
        "snippets/<int:pk>/highlight/",
        views.SnippetHighlight.as_view(),
        name="snippet-highlight",
    ),  
    path("users/", views.UserList.as_view(), name="user-list"),
    path("users/<int:pk>/", views.UserDetail.as_view(), name="extendeduser-detail"),
    path("session/", views.login_user),
    path('token/', obtain_auth_token),
    path('audits/', views.AuditList.as_view(), name="audit-list"),
    path('audits/<int:pk>/', views.AuditDetail.as_view(), name="audit-detail"),
    path("", views.api_root),
]

urlpatterns = format_suffix_patterns(urlpatterns)
