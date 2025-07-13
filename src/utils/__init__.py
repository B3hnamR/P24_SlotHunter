# حذف import مستقیم برای جلوگیری از circular import
__all__ = ['Config', 'setup_logger']

def __getattr__(name):
    if name == 'Config':
        from .config import Config
        return Config
    elif name == 'setup_logger':
        from .logger import setup_logger
        return setup_logger
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")