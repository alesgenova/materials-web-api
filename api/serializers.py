
from rest_framework import serializers
from api.models import Compound, ScalarProperty, TextProperty
from api.utils import sanitize_value


class PropertySerializer(serializers.Serializer):
    """
        Properties portion of a Compound object, used in
        /data/add/ , /data/batchadd/ , /data/search/
    """
    name = serializers.CharField()
    value = serializers.CharField()


class PropertyQuerySerializer(serializers.Serializer):
    """
        Properties portion of a /data/search request body
    """
    name = serializers.CharField()
    value = serializers.CharField()
    logic = serializers.CharField()


class CompoundNameSerializer(serializers.Serializer):
    """
        Compound portion of a /data/search request body
    """
    value = serializers.CharField()
    logic = serializers.CharField()


class CompoundSerializer(serializers.ModelSerializer):
    """
        ModelSerializer of the Compound Model, used in
        /data/add/ , /data/batchadd/ , /data/search/
    """
    properties = PropertySerializer(many=True)

    class Meta:
        model = Compound
        fields = ('compound','properties')
        # making sure the primary key is read only
        read_only_fields = ('pk',)

    def create(self, validated_data):
        """
            When we save the CompoundSerializer, we need to store not only
            the Compound Model, but also any Property attached to it.
            Overriding the create methods allows us to keep the code in the View clean and simple.
        """
        c = Compound(compound=validated_data["compound"])
        c.save()
        for prop in validated_data["properties"]:
            value = sanitize_value(prop["value"])
            if isinstance(value, float):
                p = ScalarProperty(name=prop["name"], value=value, compound=c)
            else:
                p = TextProperty(name=prop["name"], value=value, compound=c)
            p.save()
        return c


class QuerySerializer(serializers.Serializer):
    """
        Serializer for the request body of /data/search/
    """
    compound = CompoundNameSerializer(required=False)
    properties = PropertyQuerySerializer(required=False, many=True)

