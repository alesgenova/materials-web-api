def sanitize_value(value_in):
    """
      According to the assignment, all property values are passed as strings,
      but we may need to implement a different logic depending on whether the
      property is an actual string, or should be treated as a number.
      This simple helper routine does just that.
    """
    try:
        value = float(value_in)
    except ValueError:
        value = value_in
    return value