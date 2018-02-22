import numpy as np

def csv_to_compounds(csvfile):
    """
      Read compounds from the provided csvfile.
      The file is assumed to exist and be properly formatted.

      This routine can read any csv formatted in the following way

          compound_name, prop_name_1, prop_value_1, prop_name_2, prop_value_2, prop_name_3, prop_name_3, ...

      So additional properties and values can be added at will
    """
    data = np.genfromtxt(csvfile,skip_header=1, dtype=str, delimiter=",")
    compounds = []

    for i, entry in enumerate(data):
        # each line in the file is assumed to be:
        # compound_name, prop_name_1, prop_value_1, prop_name_2, prop_value_2, prop_name_3, prop_name_3, ...
        name = entry[0]
        raw_props = entry[1:]
        if len(raw_props)%2 != 0:
            raise Exception("The csv is not formatted properly")
        properties = []
        for j in range(len(raw_props)//2):
            prop = {}
            prop["name"] = raw_props[j*2]
            prop["value"] = raw_props[j*2+1]
            properties.append(prop)

        compound = {
            "compound": name,
            "properties": properties
        }
        compounds.append(compound)

    #n = min(30,len(compounds))
    return compounds#[:n]


def local_search(compounds, filter_dict):
    """
        just a throw-away routine to filter the local compounds dictionary,
        the result of the local filter, and the api filter can be compared to ensure they match.
        ensuring proper formatting is out of the scope of this, so ensure filter_dict is always valid
    """
    matches = []
    for c in compounds:
        match = True
        if "properties" in filter_dict:
            for prop in filter_dict["properties"]:
                value = _sanitize_value(prop["value"])
                if isinstance(value, float):
                    match = _scalar_prop_match(c, prop)
                else:
                    match = _text_prop_match(c, prop)
        
                if not match: break # if any of the properties don't match no need to look further

        if match and "compound" in filter_dict:
            # if there is a name in the query, add it to the QS filter
            match = _name_match(c, filter_dict["compound"])
        
        if match: matches.append(c)
    return matches
        
        
def _name_match(compound, rule):
    match = True
    if rule["logic"] == "eq":
        match = compound["compound"] == rule["value"]
    elif rule["logic"] == "startswith":
        match = compound["compound"].startswith(rule["value"])
    elif rule["logic"] == "endswith":
        match = compound["compound"].endswith(rule["value"])
    elif rule["logic"] == "contains":
        match = rule["value"] in compound["compound"]
    # anything else stays true
    #print(compound, rule, match)
    #print()
    return match
    

def _text_prop_match(compound, rule):
    if rule["logic"] == "any": return True
    
    match = True
    compound_prop = _get_prop(compound, rule["name"])
    
    # this compound doesn't even have the requested prop
    if compound_prop is None: return False
    
    if rule["logic"] == "eq":
        match = compound_prop["value"] == rule["value"]
    elif rule["logic"] == "contains":
        match = rule["value"] in compound_prop["value"]
    #print(compound_prop, rule, match)
    #print()
    return match
    

def _scalar_prop_match(compound, rule):
    if rule["logic"] == "any": return True
    
    match = True
    compound_prop = _get_prop(compound, rule["name"])
    
    # this compound doesn't even have the requested prop
    if compound_prop is None: return False
    
    rule_val = _sanitize_value(rule["value"])
    prop_val = _sanitize_value(compound_prop["value"])
    if rule["logic"] == "eq":
        match = rule_val == prop_val
    elif rule["logic"] == "gte":
        match = prop_val >= rule_val
    elif rule["logic"] == "gt":
        match = prop_val > rule_val
    elif rule["logic"] == "lte":
        match = prop_val <= rule_val
    elif rule["logic"] == "lt":
        match = prop_val < rule_val
    #print(compound, rule, match)
    #print()
    return match

def _get_prop(compound, prop_name):
    compound_prop = None
    for prop in compound["properties"]:
        if prop["name"] == prop_name:
            compound_prop = prop
            break
    return compound_prop

def _sanitize_value(value_in):
    """
      According to the assignment, all property values are passed as strings,
      but we may need to implement a different logic depending on whether the
      property is an actual string, or should be treated as a number.
      This simple helper routine does just that.
    """
    try:
        value = float(value_in)
    except ValueError:
        value = str(value_in)
    return value