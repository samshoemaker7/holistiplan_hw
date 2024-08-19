from snippets.models import ExtendedUser
from rest_framework import serializers
from snippets.models import Snippet, Audit, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.HyperlinkedModelSerializer): 
    owner = serializers.ReadOnlyField(source="owner.username")
    highlight = serializers.HyperlinkedIdentityField(  
        view_name="snippet-highlight", format="html"
    )

    class Meta:
        model = Snippet
        fields = (
            "url",
            "id",
            "highlight",
            "title",
            "code",
            "linenos",
            "language",
            "style",
            "owner",
        )  

class UserSerializer(serializers.HyperlinkedModelSerializer):  
    snippets = serializers.HyperlinkedRelatedField(  
        many=True, view_name="snippet-detail", read_only=True
    )

    class Meta:
        model = ExtendedUser
        fields = ("url", "id", "username", "snippets")

class AuditSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Audit
        fields = (
            "model_name",
            "object_id",
            "action",
            "timestamp",
            "username"
        )