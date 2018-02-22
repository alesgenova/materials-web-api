# Software Engineer Challenge

[![pipeline status](https://gitlab.com/ales.genova/materials-web-api/badges/master/pipeline.svg)](https://gitlab.com/ales.genova/materials-web-api/commits/master)

A basic Web API to add and materials data to a database, and then filter them by their name and/or properties.

Endpoints and Request body was provided by the challenge, everything else was implemented from scratch unsing `Django REST Framework`

## Readme Index
- [Code Structure](#code-structure)
- [Api Enpoints](#api-endpoints)
- [Install and Deploy](#install-and-deploy)
- [Interactive Testing](#interactive-testing)
- [Automated Testing](#automated-testing)
- [Models](#models-see-apimodelspy)
  - [Compound](#the-compound-model)
  - [Property](#the-scalarproperty-and-textproperty-models)
- [Serializers](#serializers-see-apiserializerspy)
- [Views](#views-see-apiviewspy)

## Stack
- Python 3
- Django REST Framework

## Code Structure

The relevant source code of the Web API is located at the following locations:
- `api/models.py` : Definition of the models of the relational database.
- `api/urls.py` : Define the available endpoints, and match them to the relevant View classes.
- `api/views.py` : Where the actual logic of each view is implemented. All the views inherit from Django's `GenericAPIView`.
- `api/serializers.py` : Definition of the serializers that will ensure the body of each request (both inbound and outbound) is formatted appropriately.
- `api/filters.py` : Implement the logic to filter the compounds. Given a set of compounds as input (all compounds, normally) return a subset that matches the give query.

Everything else is boilerplate code autogenerated by the Django CLI.


## API Endpoints
- `/data/add/` `POST`
  - Request Body: `CompoundSerializer`
  - Response Body: `CompoundSerializer`
  - Expected Response Status: `201`
  - Notes: If we are uploading a large number of compounds, this can be very inefficient: we make one HTTP request and one database call per compound. To mitigate this, I have implemented `/data/batchadd/`, that sends all the data at once, and is able to `bulk_create` all the compounds in the database at once (if using `PostgreSQL`)

- `/data/batchadd/` `POST`
  - Request Body: Array of `CompoundSerializer`
  - Response Payload: `None`
  - Expected Response Status: `201`

- `/data/search/` `POST`
  - Request Payload: `QuerySerializer`
  - Response Payload: Array of `CompoundSerializer`
  - Expected Response Status: `200`

- `/data/clear/` `POST`
  - Request Payload: `None`
  - Response Payload: `None`
  - Expected Response Status: `204`
  - Notes: This wipes all the entries from the database, implemented just to make debugging easier.


## Install and Deploy
For your convenience, the Web API is up and running at `https://notAvailableAnymore` .

If you wish to install the Web API locally, follow these minimal steps (Anaconda is assumed to be available on the computer):

```bash
# Create the Python virtual environment and activate it
conda create -n materials_env
source activate materials_env
conda install -n materials_env pip

# Install all the required Python packages
pip install -r requirements.txt
# initialize the tables in the database
python manage.py makemigrations api
python manage.py migrate
# OPTIONAL: create a superuser to access the models through the web interface
python manage.py createsuperuser

# Run the development webserver
python manage.py runserver
# the API is now available at http://localhost:8000
```


## Interactive Testing
Simple examples to programmatically probe the Web API using the `request` package are in the Jupyter Notebook `test_api.ipynb`.

In the notebook I read the compounds from the provided `data.csv` file, and load them up to the API using `/data/add/` (1 HTTP request for each compound, slow), and `/data/batchadd/` (All compounds in a single HTTP request, much faster).

I also show how the search results provided by the Web API match results evaluated locally.


## Automated Testing
Unit tests equivalent to the examples shown in the Jupyte Notebook are in the `tests` folder. To execute them:
```bash
pytest ./tests/
```
These tests are included in the `gitlab-ci` pipeline, and are executed each time changes are pushed to the repository.


## Models (see `api/models.py`)

`Compounds` are linked to their `Properties` through a `ForeignKey` (OneToMany relation). This way we don't have to hard code the names of each individual property we may need now or in the future. As a result of this design choice, the Web API is already capable of storing and searching compounds with any type of numerical and/or textual property, and not just `band gap` or `color`.


### The `Compound` model

```Python
class Compound(models.Model):
    compound = models.CharField(max_length=127)

    def __str__(self):
      return "{}".format(self.compound)

    @property
    def properties(self):
      """
        useful property of the Compound Model to list all of its properties
        no matter what their type is.
        Used by the CompoundModelSerializer.
      """
      props = []
      for p in self.scalarproperty.all():
        props.append(p)
      for p in self.textproperty.all():
        props.append(p)
      return props
```


### The `ScalarProperty` and `TextProperty` models

```python
class BaseProperty(models.Model):
    """
      This is an abstract class, that is never actually used in the code.
      It serves as a blue print for the actual implementations of ScalarProperty and TextProperty,
      of whichever other type of property we will want to add in the future.
    """
    compound = models.ForeignKey(Compound, related_name='%(class)s', on_delete=models.CASCADE)
    name = models.CharField(max_length=127)

    class Meta:
        abstract = True

    def __str__(self):
      return "{} - {}".format(self.compound, self.name)

class ScalarProperty(BaseProperty):
    value = models.FloatField()

    def __str__(self):
      return "{} - {}: {}".format(self.compound, self.name, self.value)

class TextProperty(BaseProperty):
    value = models.CharField(max_length=127)

    def __str__(self):
      return "{} - {}: {}".format(self.compound, self.name, self.value)
```


## Serializers (see `api/serializers.py`)
The `Serializers` defined here are used in the `Views` below to ensure that the body of each request (both inbound and outbound) is formatted appropriately.

```python
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

```


## Views (see `api/views.py`)

The actual logic executed when a request is made to one of the API endpoints.

```python
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
```

