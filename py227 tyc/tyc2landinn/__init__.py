

try:
    from .tyc_to_landinn import main
except ImportError:
    from .tyc_to_landinn import start_execute as main