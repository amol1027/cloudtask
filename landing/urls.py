from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # TODO: Add more landing pages
    # path('about/', views.AboutView.as_view(), name='about'),
    # path('features/', views.FeaturesView.as_view(), name='features'),
    # path('pricing/', views.PricingView.as_view(), name='pricing'),
    # path('contact/', views.ContactView.as_view(), name='contact'),
]
