from django.contrib import admin
from .models import Club, Employee, LiaisonOfficer, AttendanceRecord,  DocumentRequest
import logging
from django.contrib.auth.models import Group


from datetime import datetime, timedelta
from django.contrib.admin import SimpleListFilter


#for checking and adding the groups
logger = logging.getLogger(__name__)

# Add groups if not already done
liaison_officer_group, _ = Group.objects.get_or_create(name='Liaison Officer')
hr_manager_group, _ = Group.objects.get_or_create(name='HR Manager')


#for adding a filter in the employee last paid month(adding the 2 month, 3 month and 4 month) 
class LastPaidMonthFilter(SimpleListFilter):
    title = 'By last paid month'  # Display name for the filter
    parameter_name = 'last_paid_month'  # Query parameter in the URL

    def lookups(self, request, model_admin):
        # Define filter options
        return [
            ('any_date', 'Any date'),
            ('today', 'Today'),
            ('past_7_days', 'Past 7 days'),
            ('this_month', 'This month'),
            ('2_months', '2 months'),
            ('3_months', '3 months'),
            ('4_months', '4 months'),
            ('this_year', 'This year'),    
            ('no_date', 'No date'),
            ('has_date', 'Has date'),
        ]

    def queryset(self, request, queryset):
        # Filter logic based on the selected option
        value = self.value()
        today = datetime.today()

        if value == 'today':
            return queryset.filter(last_paid_month=today.date())
        elif value == 'past_7_days':
            return queryset.filter(last_paid_month__gte=today - timedelta(days=7))
        elif value == 'this_month':
            return queryset.filter(last_paid_month__month=today.month, last_paid_month__year=today.year)
        elif value == 'this_year':
            return queryset.filter(last_paid_month__year=today.year)
        elif value == '2_months':
            return queryset.filter(last_paid_month__gte=today - timedelta(days=60))
        elif value == '3_months':
            return queryset.filter(last_paid_month__gte=today - timedelta(days=90))
        elif value == '4_months':
            return queryset.filter(last_paid_month__gte=today - timedelta(days=120))
        elif value == 'no_date':
            return queryset.filter(last_paid_month__isnull=True)
        elif value == 'has_date':
            return queryset.exclude(last_paid_month__isnull=True)
        return queryset  # Default: return unfiltered queryset










@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'club', 'start_date', 'last_paid_month')
    list_filter = ('role', 'club', 'start_date', LastPaidMonthFilter)
    search_fields = ('full_name', 'phone_number', 'email')

@admin.register(LiaisonOfficer)
class LiaisonOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'club')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'club', 'date', 'present', 'entrance_time', 'exit_time', 'exit_reason')
    list_filter = ('employee__club', 'present', 'date')
    search_fields = ('employee__full_name', 'employee__phone_number')
    date_hierarchy = 'date'




    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:  # Only filter for non-superusers
            try:
                # Get the logged-in liaison officer's club
                liaison_officer = LiaisonOfficer.objects.get(user=request.user)
                club = liaison_officer.club

                # Filter the employee field to show only employees in the same club
                form.base_fields['employee'].queryset = Employee.objects.filter(club=club)
            except LiaisonOfficer.DoesNotExist:
                # If the user is not a liaison officer, show no employees
                form.base_fields['employee'].queryset = Employee.objects.none()

        return form




    def get_queryset(self, request):
    
        """
        Filter attendance records based on the user's role:
        - Liaison officers see only records for their club.
        - HR managers and superusers see all records.
        """
    
        qs = super().get_queryset(request)

        # Check if the user is a superuser or HR Manager
        if request.user.is_superuser or request.user.groups.filter(name="HR Manager").exists():
            logger.debug(f"Superuser or HR Manager: {request.user}")
            return qs

        # Check if the user is a Liaison Officer
        if request.user.groups.filter(name="Liaison Officer").exists():
           try:
               
                # Fetch the login Liaison Officer
                liaison_officer = LiaisonOfficer.objects.get(user=request.user)
                # Fetch the club employees assigned to this Liaison Officer
                #employees=Employee.objects.get(employee__club=liaison_officer.club)


                # Filter attendance records for employees in the same club
                return qs.filter(employee__club=liaison_officer.club)
           except LiaisonOfficer.DoesNotExist:
                return qs.none()  # If the liaison officer is not linked to a club, return no records


       # Default to no records for other users
        logger.debug(f"User not authorized to view records: {request.user}")
        return qs.none()
  








    


    fieldsets = (
        (None, {
            'fields': ('employee', 'date', 'present', 'entrance_time', 'exit_time', 'exit_reason')
        }),
    )



    def club(self, obj):
        """Display the club name in the list view."""
        return obj.employee.club.name
    club.admin_order_field = 'employee__club'

    fieldsets = (
        (None, {
            'fields': ('employee', 'date', 'present', 'entrance_time', 'exit_time', 'exit_reason')
        }),
    )










@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ('requested_by', 'employee', 'document_type', 'status', 'request_date')
    list_filter = ('status', 'request_date','club')
    search_fields = ('requested_by__username', 'employee__full_name', 'document_type')

    def get_queryset(self, request):
        """
        Limit the queryset based on the user's role:
        - HR Managers see all requests.
        - Club Managers see only their requests.
        """
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='HR Manager').exists():
            return qs  # HR Managers can view all requests
        elif request.user.groups.filter(name='Club Manager').exists():
            return qs.filter(requested_by=request.user)  # Club Managers see only their requests
        return qs.none()  # Default: No access

    def has_change_permission(self, request, obj=None):
        # Allow HR Managers to edit all requests, Club Managers only their own
        if request.user.groups.filter(name='HR Manager').exists():
            return True
        if obj and request.user == obj.requested_by:
            return True
        return False

    def save_model(self, request, obj, form, change):
        # Automatically set the requester to the logged-in user
        if not change:
            obj.requested_by = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # Restrict add permission to the Club Manager group
        return request.user.groups.filter(name='Club Manager').exists()

    #def has_change_permission(self, request, obj=None):
        # Restrict change permission to HR managers or admins
     #   return request.user.is_superuser or request.user.groups.filter(name='HR Manager').exists()

    def has_delete_permission(self, request, obj=None):
        # Restrict delete permission to superusers
        return request.user.is_superuser
