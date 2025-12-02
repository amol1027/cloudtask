from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class IndexView(TemplateView):
    """Landing page view"""
    template_name = 'landing/index.html'


# TODO: Add more landing pages as needed:
# - AboutView
# - FeaturesView
# - PricingView
# - ContactView
