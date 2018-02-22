from django.db.models import Q
from api.models import Compound, ScalarProperty, TextProperty
from api.utils import sanitize_value


def process_filter(compounds, query):
    """
        Inputs:
          - compounds:  QuerySet containing the input compounds (possibly all the compounds in the DB)
          - query:      An object containing the filter logic, with the following format:
                        query = {
                            "compound": {
                                "value": "Pb",
                                "logic": "contains"
                            },
                            "properties": [
                                {
                                    "name": "Band gap",
                                    "value": "2.5",
                                    "logic": "gte"
                                },
                                {
                                    "name": "Color",
                                    "value": "Red",
                                    "logic": "contains"
                                },
                                {
                                    "name": "Density",
                                    "value": "25.0",
                                    "logic": "lt"
                                }
                            ]
                        } 
        Output:
          - filtered_compounds: A subset of the compounds given as input
    """

    # Initialize the QS object. 
    # It will allow us to sequentially build extremely flexible queries
    # By concatenating smaller queries connected to each other by Q.AND or Q.OR logic
    # Once QS is complete, we can use it to filter the compounds given as input
    QS = Q()

    if "properties" in query:
        # if there are properties in the query, add them to the QS filter
        for prop in query["properties"]:
            value = sanitize_value(prop["value"])
            if isinstance(value, float):
                _scalarPropertyFilter(QS, prop)
            else:
                _textPropertyFilter(QS, prop)

    if "compound" in query:
        # if there is a name in the query, add it to the QS filter
        _compoundNameFilter(QS, query["compound"])
    
    return compounds.filter(QS)
    
            
    

def _scalarPropertyFilter(QS, property):
    logic = property["logic"].lower()
    value = float(property["value"])
    name = property["name"]

    if logic=="gt":
        pks = ScalarProperty.objects.filter(name=name, value__gt=value).values_list("compound__pk",flat=True)
    elif logic=="lt":
        pks = ScalarProperty.objects.filter(name=name, value__lt=value).values_list("compound__pk",flat=True)
    elif logic=="gte":
        pks = ScalarProperty.objects.filter(name=name, value__gte=value).values_list("compound__pk",flat=True)
    elif logic=="lte":
        pks = ScalarProperty.objects.filter(name=name, value__lte=value).values_list("compound__pk",flat=True)
    elif logic=="eq":
        pks = ScalarProperty.objects.filter(name=name, value=value).values_list("compound__pk",flat=True)
    else:
        return
    QS.add(Q(pk__in=pks), Q.AND)
    return


def _textPropertyFilter(QS, property):
    logic = property["logic"].lower()
    value = property["value"]
    name = property["name"]

    if logic=="eq":
        pks = TextProperty.objects.filter(name=name, value=value).values_list("compound__pk",flat=True)
    elif logic=="contains":
        pks = TextProperty.objects.filter(name=name, value__contains=value).values_list("compound__pk",flat=True)
        
    else:
        return
    QS.add(Q(pk__in=pks), Q.AND)
    return

def _compoundNameFilter(QS, nameFilter):
    logic = nameFilter["logic"].lower()
    value = nameFilter["value"]

    if logic == "eq":
        QS.add(Q(compound=value),Q.AND)
        #compounds = compounds.filter(compound=value)
    elif logic == "contains":
        QS.add(Q(compound__contains=value),Q.AND)
        #compounds = compounds.filter(compound__contains=value)
    elif logic == "startswith":
        QS.add(Q(compound__startswith=value),Q.AND)
        #compounds = compounds.filter(compound__startswith=value)
    elif logic == "endswith":
        QS.add(Q(compound__endswith=value),Q.AND)
        #compounds = compounds.filter(compound__endswith=value)
    
    return