#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CSP_1.settings')
django.setup()

from django.contrib.auth.models import User
from laba_1.models import UserGroup, Athlete, Competition, Distance, Result

print('\n=== LOADED USERS ===')
for u in User.objects.all():
    group = u.profile.group.name if hasattr(u, 'profile') and u.profile.group else 'N/A'
    print(f'{u.username}: {u.email} (group: {group})')

print('\n=== USER GROUPS ===')
for g in UserGroup.objects.all():
    print(f'- {g.name}: {g.description}')

print('\n=== STATISTICS ===')
print(f'Athletes: {Athlete.objects.count()}')
print(f'Competitions: {Competition.objects.count()}')
print(f'Distances: {Distance.objects.count()}')
print(f'Results: {Result.objects.count()}')

print('\n✓ Database loaded successfully!')
print('\nTest credentials:')
print('  admin / admin')
print('  coach1 / coach1')
print('  athlete1 / athlete1')
print('  athlete2 / athlete2')
print('  athlete3 / athlete3')
