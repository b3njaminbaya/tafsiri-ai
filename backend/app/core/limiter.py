from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance imported by main.py (to register the exception
# handler/middleware) and by individual routes (to apply @limiter.limit(...)).
# Living in its own module avoids a main.py <-> routes circular import.
limiter = Limiter(key_func=get_remote_address)
