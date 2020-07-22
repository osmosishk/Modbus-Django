from django import forms
from .models import Slaves
from .models import Address
from .models import Setting


class SlavesForm(forms.ModelForm):

    class Meta:
        model = Slaves
        fields = "__all__"

class SettingForm(forms.ModelForm):

    class Meta:
        model = Setting
        fields = "__all__"

class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = "__all__"