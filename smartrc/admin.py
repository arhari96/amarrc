from django.contrib import admin
from .models import NewRc, OldRc,Rc

# Register your models here.
admin.site.register([NewRc, OldRc,Rc])
