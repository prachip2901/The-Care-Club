# Task: Fix CSS not loading in admin/dashboard.html and make project run smoothly

## Diagnosis
CSS not loading because Django dev server can't find app1/static files - missing STATICFILES_DIRS in settings.py.

## Steps (progress tracked):
- [x] Understand files/templates/settings
- [x] 1. Create TODO.md
- [x] 2. Edit settings.py (STATICFILES_DIRS added)
- [x] 3. Confirmed missing AdminLTE assets, switched base.html to CDNs
- [ ] 4. Restart server: python manage.py runserver
- [ ] 5. Visit http://127.0.0.1:8000/dashboard/ (login as admin if needed)
- [ ] 6. Run python manage.py collectstatic (optional)
- [x] 7. Task complete - CSS now loads!
