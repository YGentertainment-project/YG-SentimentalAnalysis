from attr import field
from .models import KeywordGroup, Keyword, Group, GroupKeyword, GroupSchedule, GroupUser
from rest_framework import serializers


class KeywordGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordGroup
        fields = "__all__"


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = "__all__"
    
    def to_representation(self, instance):
        self.fields["keywordgroup"] = KeywordGroupSerializer(read_only=True)
        return super(KeywordGroupSerializer, self).to_representation(instance)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class GroupKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupKeyword
        fields = "__all__"
    
    def to_representation(self, instance):
        self.fields["group"] = GroupSerializer(read_only=True)
        return super(GroupSerializer, self).to_representation(instance)


class GroupScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSchedule
        fields = "__all__"
    
    def to_representation(self, instance):
        self.fields["group"] = GroupSerializer(read_only=True)
        return super(GroupSerializer, self).to_representation(instance)


class GroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupUser
        fields = "__all__"
    
    def to_representation(self, instance):
        self.fields["group"] = GroupSerializer(read_only=True)
        return super(GroupSerializer, self).to_representation(instance)
