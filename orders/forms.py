from django import forms


class DistanceForm(forms.Form):
    source = forms.CharField(
        label="Source Address",
        max_length=512,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    destination = forms.CharField(
        label="Destination Address",
        max_length=512,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
