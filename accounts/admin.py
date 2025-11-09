"""
File: admin.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: Register users to admin panel.
"""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User)
