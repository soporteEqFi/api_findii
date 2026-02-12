"""
Excepciones y utilidades para manejar errores de conectividad con Supabase.
Permite devolver 503 Service Unavailable en lugar de 500 cuando la BD no está disponible.
"""
import sys

# Excepciones de conectividad (Supabase usa httpx internamente)
_SUPABASE_CONNECTIVITY_ERRORS = ()

try:
    import httpx
    _SUPABASE_CONNECTIVITY_ERRORS += (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
    )
except ImportError:
    pass

try:
    import requests
    _SUPABASE_CONNECTIVITY_ERRORS += (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    )
except ImportError:
    pass

# Errores de red a nivel de sistema (connection refused, network unreachable, etc.)
_SUPABASE_CONNECTIVITY_ERRORS += (
    ConnectionRefusedError,
    TimeoutError,
)


def is_supabase_connectivity_error(exc: BaseException) -> bool:
    """
    Indica si la excepción corresponde a un error de conectividad con Supabase
    (BD caída, timeout, red inaccesible, etc.).
    """
    exc_type = type(exc)
    for err_type in _SUPABASE_CONNECTIVITY_ERRORS:
        if err_type and issubclass(exc_type, err_type):
            return True
    # Mensajes típicos cuando Supabase está caído
    msg = str(exc).lower()
    if any(k in msg for k in ("connection", "refused", "timed out", "timeout", "unreachable", "dns")):
        return True
    return False


def get_supabase_error_message(exc: BaseException) -> str:
    """Mensaje amigable para el cliente cuando Supabase no está disponible."""
    return "El servicio de base de datos no está disponible temporalmente. Intenta de nuevo en unos minutos."
