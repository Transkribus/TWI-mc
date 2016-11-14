## PRODUCTION
try:
    from mc.settings.production import *
except ImportError:
    pass

## DEVELOPMENT
try:
    from mc.settings.development import *
except ImportError:
    pass
## LOCAL
try:
    from mc.settings.local import *
except ImportError:
    pass

