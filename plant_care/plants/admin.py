from django.contrib import admin
from .models import Plant, CareTask, CareLog


class CaseInsensitiveSearchAdmin(admin.ModelAdmin):
    def get_search_results(self, request, queryset, search_term):
        if not search_term.strip():
            return queryset, False

        search_words = search_term.casefold().split()
        matching_ids = []

        for obj in queryset:
            values = []

            for field in self.search_fields:
                value = obj

                for attr in field.split('__'):
                    value = getattr(value, attr, '')

                values.append(str(value or '').casefold())

            if all(
                any(word in value for value in values)
                for word in search_words
            ):
                matching_ids.append(obj.pk)

        return queryset.filter(pk__in=matching_ids), False


@admin.register(Plant)
class PlantAdmin(CaseInsensitiveSearchAdmin):
    list_display = ['id', 'name', 'species', 'owner', 'watering_interval', 'last_watered']
    list_filter = ['species', 'owner']
    search_fields = ['name', 'species', 'owner__username']
    ordering = ('name',)
    list_per_page = 10


@admin.register(CareTask)
class CareTaskAdmin(CaseInsensitiveSearchAdmin):
    list_display = ['id', 'plant', 'task_type', 'scheduled_date', 'priority', 'is_completed']
    list_filter = ['task_type', 'priority', 'is_completed', 'scheduled_date']
    search_fields = ['plant__name', 'notes']
    ordering = ('scheduled_date', 'priority')
    list_per_page = 10


@admin.register(CareLog)
class CareLogAdmin(CaseInsensitiveSearchAdmin):
    list_display = ['id', 'plant', 'care_type', 'performed_at', 'task']
    list_filter = ['care_type', 'performed_at']
    search_fields = ['plant__name', 'notes']
    ordering = ('-performed_at',)
    list_per_page = 10


admin.site.site_header = "PlantCare — Адміністрування"
admin.site.site_title = "PlantCare Admin"
admin.site.index_title = "Панель керування PlantCare"
