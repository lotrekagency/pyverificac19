from . import service
import pook


@pook.on
def run_all():
    service.run_setup()
