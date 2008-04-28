import django.newforms as forms

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = forms.CharField()
    subject = forms.CharField()
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))