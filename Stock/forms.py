from django import forms
from .models import StockCheck,Distribution
import logging

logger = logging.getLogger(__name__)



class StockCheckForm(forms.ModelForm):
    class Meta:
        model = StockCheck
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        logger.info(f"Request: {request}")
        super().__init__(*args, **kwargs)

        self.fields['distribution'].queryset = Distribution.objects.none()
        print('the ttttttttt',request)
        if request and hasattr(request.user, 'userprofile'):
            user_profile = request.user.userprofile
            logger.info(f"User Profile: {user_profile}")
            if user_profile.club:
                self.fields['distribution'].queryset = Distribution.objects.filter(club=user_profile.club)
            else:
                self.fields['distribution'].queryset = Distribution.objects.all()