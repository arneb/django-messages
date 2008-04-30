import django.newforms as forms

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = forms.CharField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"), widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))