from django.db import models

# Create your models here.
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

