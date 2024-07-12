import os

from hdmf.utils import docval, get_docval

from pynwb import get_class, load_namespaces, register_class

try:
    from importlib.resources import files
except ImportError:
    # TODO: Remove when python 3.9 becomes the new minimum
    from importlib_resources import files

# Get path to the namespace.yaml file with the expected location when installed not in editable mode
__location_of_this_file = files(__name__)
__spec_path = __location_of_this_file / "spec" / "ndx-extracellular-channels.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / "ndx-extracellular-channels.namespace.yaml"

# Load the namespace
load_namespaces(str(__spec_path))

ProbeInsertion = get_class("ProbeInsertion", "ndx-extracellular-channels")
ContactsTable = get_class("ContactsTable", "ndx-extracellular-channels")
ProbeModel = get_class("ProbeModel", "ndx-extracellular-channels")
Probe = get_class("Probe", "ndx-extracellular-channels")
ChannelsTable = get_class("ChannelsTable", "ndx-extracellular-channels")
AutoExtracellularSeries = get_class("ExtracellularSeries", "ndx-extracellular-channels")

init_dv = [dv for dv in get_docval(AutoExtracellularSeries.__init__) if dv["name"] != "unit"]


@register_class("ExtracellularSeries", "ndx-extracellular-channels")
class ExtracellularSeries(AutoExtracellularSeries):

    @docval(*init_dv)
    def __init__(self, **kwargs):
        # NOTE: "unit" is a required constructor argument in the auto-generated class
        # but it's value is fixed to "microvolts"
        kwargs["unit"] = "microvolts"
        super().__init__(**kwargs)


from .io import from_probeinterface, to_probeinterface

__all__ = (
    "ProbeInsertion",
    "ContactsTable",
    "ProbeModel",
    "Probe",
    "ChannelsTable",
    "ExtracellularSeries",
    "from_probeinterface",
    "to_probeinterface",
)

# Remove these functions from the package
del load_namespaces, get_class, init_dv
