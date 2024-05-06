# forms.py
from django import forms

class AddScholarshipForm(forms.Form):
    Name = forms.CharField(max_length=255)
    Eligibility = forms.CharField(widget=forms.Textarea)
    Eligible = forms.CharField(widget=forms.Textarea)
    Contacts_offline_applications = forms.CharField(widget=forms.Textarea)
    Special_Categories = forms.CharField(widget=forms.Textarea)
    Scholarship_Fellowship = forms.CharField(max_length=255)
    Level = forms.CharField(max_length=255)
    State = forms.CharField(max_length=255, required=False)
    Application_Period = forms.CharField(max_length=255)
    Links_online_application = forms.URLField()
