import os
from pynwb import load_namespaces, get_class

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
ExtracellularSeries = get_class("ExtracellularSeries", "ndx-extracellular-channels")

# NOTE: `widgets/tetrode_series_widget.py` adds a "widget"
# attribute to the TetrodeSeries class. This attribute is used by NWBWidgets.
# Delete the `widgets` subpackage or the `tetrode_series_widget.py` module
# if you do not want to define a custom widget for your extension neurodata
# type.

# Remove these functions from the package
del load_namespaces, get_class
