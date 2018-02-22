from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics

from .serializers import CompoundSerializer, QuerySerializer
from .models import Compound, ScalarProperty, TextProperty
from .filters import process_filter


class AddCompound(generics.GenericAPIView):
    """
        Api Endpoint:   /data/add/
        HTTP Methods:   POST
        Request Body:   CompoundSerializer
        Response Body:  CompoundSerializer
        Action:         The request body contains a Compound and its properties.
                        Save it to the database after ensuring the format is correct.
    """
    # serializer that will ensure validity of the request body
    serializer_class = CompoundSerializer
    # definition of queryset or get_queryset is required by Django
    # even if we don't actually need it.
    queryset = []

    def post(self, request, *args, **kwargs):
        compound_serializer = self.serializer_class(data=request.data)
        # validate request body
        compound_serializer.is_valid(raise_exception=True)
        # Save the compound to the database
        compound = compound_serializer.save()
        return Response(self.serializer_class(compound).data, status=status.HTTP_201_CREATED)


class AddCompounds(generics.GenericAPIView):
    """
        Api Endpoint:   /data/batchadd/
        HTTP Methods:   POST
        Request Body:   CompoundSerializer (array)
        Response Body:  Empty
        Action:         The request body contains a list of Compounds and their properties.
                        Save them to the database after ensuring the format is correct.
    """
    # serializer that will ensure validity of the request body
    serializer_class = CompoundSerializer
    # definition of queryset or get_queryset is required by Django
    # even if we don't actually need it.
    queryset = []

    def post(self, request, *args, **kwargs):
        # validate request body against the serializer,
        # and return a 400 response if validation fails
        compounds_serializer = self.serializer_class(data=request.data, many=True)
        compounds_serializer.is_valid(raise_exception=True)
        # Save the compounds to the database
        compounds_serializer.save()
        return Response({}, status=status.HTTP_201_CREATED)


class RemoveAll(generics.GenericAPIView):
    """
        Api Endpoint:   /data/clear/
        HTTP Methods:   POST
        Request Body:   Empty
        Response Body:  Empty
        Action:         Remove all the compounds from the database.
                        Implemented just to make it easier to start over.
    """
    serializer_class = None

    def get_queryset(self, *args, **kwargs):
      return Compound.objects.all()

    def post(self, request, *args, **kwargs):
        compounds = self.get_queryset()
        compounds.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class SearchCompounds(generics.GenericAPIView):
    """
        Api Endpoint:   /data/search/
        HTTP Methods:   POST
        Request Body:   QuerySerializer
        Response Body:  CompoundSerializer (array)
        Action:         Given a set of filter rules on the name and properties,
                        return all the compounds in the database that match.
    """
    serializer_class = QuerySerializer

    def get_queryset(self, filter_serializer, *args, **kwargs):
        # we start from all the compounds
        compounds = Compound.objects.all()
        # and filter them down according to the filter in the request body
        compounds = process_filter(compounds, filter_serializer.validated_data)
        return compounds

    def post(self, request, *args, **kwargs):
        # validate request body against the serializer,
        # and return a 400 response if validation fails
        filter_serializer = self.serializer_class(data=request.data)
        filter_serializer.is_valid(raise_exception=True)
        # get the compounds that match the filter
        compounds = self.get_queryset(filter_serializer)
        # serialize and return them
        output = CompoundSerializer(compounds, many=True)
        return Response(output.data, status=status.HTTP_200_OK)

        