from django.http import HttpResponse
from django.core.urlresolvers import reverse
# Create your views here.
def home(request):
	if request.user.is_active:
		return HttpResponse('<a href="{0}">inbox</a>'.format(reverse('messages_inbox')))	
	return HttpResponse('Please <a href="/admin/">login</a>.')