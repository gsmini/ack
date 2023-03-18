from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from apps.namespace import views as namespace_view
from apps.event import views as event_view
from apps.deployment import views as deployment_view

router = DefaultRouter(trailing_slash=False)
router.register(r'namespace', namespace_view.NameSpaceViewSet, basename='namespace')
router.register(r'event', event_view.EventViewSet, basename='event')
router.register(r'deployment', deployment_view.DeploymentViewSet, basename='deployment')

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'api/v1/', include(router.urls)),
]
