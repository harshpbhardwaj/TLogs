from rest_framework import serializers
from home.models import Tlogs, Tlog_body, Tlog_comment

class HexaSerializers(serializers.HyperlinkedModelSerializer):
    id=serializers.ReadOnlyField()
    class Meta:
        model=Tlogs
        fields="__all__"

class BodySerializers(serializers.HyperlinkedModelSerializer):
    id=serializers.ReadOnlyField()
    class Meta:
        model=Tlog_body
        fields="__all__"

class CommentSerializers(serializers.HyperlinkedModelSerializer):
    id=serializers.ReadOnlyField()
    class Meta:
        model=Tlog_comment
        fields="__all__"