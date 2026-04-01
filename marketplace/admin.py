from django.contrib import admin
from .models import Listing
from .models import Review
from .models import Message

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'seller', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

admin.site.register(Listing, ListingAdmin)
admin.site.register(Review)
admin.site.register(Message)