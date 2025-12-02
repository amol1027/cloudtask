from django.db import models
from django.contrib.auth.models import User

# TODO: Phase 2 - Implement Task models
# Task model should include:
# - title: CharField
# - description: TextField
# - status: CharField with choices (TODO, IN_PROGRESS, DONE)
# - priority: CharField with choices (LOW, MEDIUM, HIGH)
# - due_date: DateTimeField
# - created_at: DateTimeField (auto_now_add=True)
# - updated_at: DateTimeField (auto_now=True)
# - assigned_to: ForeignKey to User
# - created_by: ForeignKey to User
# - tags: ManyToManyField to Tag model (optional)

# Tag model should include:
# - name: CharField
# - color: CharField (hex color code)

# Placeholder for initial migrations
