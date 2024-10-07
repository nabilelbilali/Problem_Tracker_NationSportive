from django.contrib import admin
from .models import Club, Problem, UserProfile

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

    class Media:
        css = {
            'all': ('clubs/css/custom_admin.css',)  # Link to your custom CSS
        }

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('club', 'description', 'created_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.userprofile.is_supervisor:
            return qs.filter(club=request.user.userprofile.club)
        return qs


    class Media:
        css = {
            'all': ('clubs/css/custom_admin.css',)
        }

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'is_supervisor')

    class Media:
        css = {
            'all': ('clubs/css/custom_admin.css',)
        }


admin.site.site_header = "Nation Sportive"
admin.site.site_title = "Problem Tracker"
admin.site.index_title = "Welcome to the Admin Dashboard"
