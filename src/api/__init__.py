# حذف import مستقیم برای جلوگیری از circular import
__all__ = ['PazireshAPI', 'Doctor', 'Appointment']

def __getattr__(name):
    if name == 'PazireshAPI':
        from .paziresh_client import PazireshAPI
        return PazireshAPI
    elif name == 'Doctor':
        from .models import Doctor
        return Doctor
    elif name == 'Appointment':
        from .models import Appointment
        return Appointment
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")