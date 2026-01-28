from django.urls import path
from . import views

# Authentication has been disabled for this WhatsApp-based ordering system
# All user management is done through Django Admin only

urlpatterns = [
    # All authentication routes removed - system is now anonymous/session-based
    # User login, register, dashboard, password reset all removed
]
