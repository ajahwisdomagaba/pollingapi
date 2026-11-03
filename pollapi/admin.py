from django.contrib import admin
from .models import Poll, Option, Vote

# Show polls, choices, and votes on the admin site.
admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(Vote)
