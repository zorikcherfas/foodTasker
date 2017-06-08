from django import forms
from django.contrib.auth.models import User
from foodtaskerapp.models import Resturant

class UserForm(forms.ModelForm):
    email = forms.CharField(max_length = 100, required=True)
    password = forms.CharField(widget = forms.PasswordInput())
    class Meta:
        model = User
        fields = ("username" , "password", "first_name" , "last_name" , "email")

class ResturantForm(forms.ModelForm):
    class Meta:
        model = Resturant
        fields = ("name" , "phone", "address" , "logo" )
