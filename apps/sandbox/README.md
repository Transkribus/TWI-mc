# TWI-sandbox #

```bash
grep -r TODO TWI-sandbox/sandbox
grep -r FIXTHIS TWI-sandbox/sandbox
```

How to create a pull request: https://www.atlassian.com/git/tutorials/making-a-pull-request

Add to *TWI-mc/apps*.

```bash
cp -r /path/to/TWI-sandbox/sandbox /path/to/TWI-mc/apps
```

Edit *mc/urls.py*:

```python
    url(r'^sandbox/', include('apps.sandbox.urls', app_name='sandbox', namespace='sandbox')),
```

Add to *NSTALLED_APPS* in *mc/settings/development.py*.

```python
INSTALLED_APPS = [
  ...
  'sandbox',
  ...
]
```