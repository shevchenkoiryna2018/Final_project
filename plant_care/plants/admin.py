from django.contrib import admin
from .models import Plant, CareTask, CareLog


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'species', 'owner', 'watering_interval', 'last_watered']
    list_filter = ['species', 'owner']
    search_fields = ['name', 'species', 'owner_username']
    ordering = ('name',)
    list_per_page = 10


@admin.register(CareTask)
class CareTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'plant', 'task_type', 'scheduled_date', 'priority', 'is_completed']
    list_filter = ['task_type', 'priority', 'is_completed', 'scheduled_date']
    search_fields = ['plant__name', 'notes']
    ordering = ('scheduled_date', 'priority')
    list_per_page = 10


@admin.register(CareLog)
class CareLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'plant', 'care_type', 'performed_at', 'task']
    list_filter = ['care_type', 'performed_at']
    search_fields = ['plant__name', 'notes']
    ordering = ('-performed_at',)
    list_per_page = 10

