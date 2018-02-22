from django.contrib import admin

# Register your models here.
from .models import Compound, ScalarProperty, TextProperty

admin.site.register([Compound, ScalarProperty, TextProperty])

