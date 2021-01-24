"""walletmonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from apps.transactions import views as tr_views
from apps.core import views as core_views
from apps.monitor import views as monitor_views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('accounts/', include('django_registration.backends.activation.urls')),
	path('accounts/', include('django.contrib.auth.urls')),
	path('', core_views.home),
	path('home/', core_views.home),
	path('monitor/', monitor_views.monitor),
	path('graph/', monitor_views.graph),
	path('transactions/add', tr_views.add),
	path('transactions/show', tr_views.show),
	path('transactions/edit/<int:id>', tr_views.edit),
	path('transactions/update/<int:id>', tr_views.update),
	path('transactions/delete/<int:id>', tr_views.destroy),
]
