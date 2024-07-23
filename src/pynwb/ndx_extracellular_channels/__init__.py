import os
import warnings

from hdmf.utils import docval, get_docval, get_data_shape
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
AutoProbeModel = get_class("ProbeModel", "ndx-extracellular-channels")
Probe = get_class("Probe", "ndx-extracellular-channels")
AutoChannelsTable = get_class("ChannelsTable", "ndx-extracellular-channels")
AutoExtracellularSeries = get_class("ExtracellularSeries", "ndx-extracellular-channels")

probe_model_init_dv = [dv for dv in get_docval(AutoProbeModel.__init__) if dv["name"] != "name"]
probe_model_init_dv.append(
    {
        "name": "name",
        "type": str,
        "doc": "name of this ProbeModel. If not provided, this will be set to the value of ``model``",
        "default": None,
    }
)


@register_class("ProbeModel", "ndx-extracellular-channels")
class ProbeModel(AutoProbeModel):

    @docval(*probe_model_init_dv)
    def __init__(self, **kwargs):
        # If the user does not provide a name, we set it to the value of "model"
        if kwargs.get("name") is None:
            kwargs["name"] = kwargs["model"]
        super().__init__(**kwargs)


channels_table_init_dv = [dv for dv in get_docval(AutoChannelsTable.__init__) if dv["name"] != "target_tables"]


@register_class("ChannelsTable", "ndx-extracellular-channels")
class ChannelsTable(AutoChannelsTable):

    @docval(*channels_table_init_dv)
    def __init__(self, **kwargs):
        # DynamicTable has an optional constructor argument "target_tables"
        # that sets the target tables for the foreign keys in the table after initializing
        # each column. Since `probe`, `Probe.probe_model` and `ProbeModel.contacts_table` are all
        # required constructor arguments, we can set the target tables here.
        kwargs["target_tables"] = {
            "contact": kwargs["probe"].probe_model.contacts_table,
        }
        super().__init__(**kwargs)

    @docval(*get_docval(AutoChannelsTable.add_row), allow_extra=True)
    def add_row(self, **kwargs):
        # "reference_contact" is an optional column that is only added if the column is not already present.
        # When it is added, we need to make sure that the target table is set correctly.
        # So here, if the user supplies a "reference_contact" value and the column is not present,
        # we set the target table for the column before we add the row
        # (which would create the column without the target table).
        # This may be handled automatically in the future by HDMF.
        if "reference_contact" in kwargs and "reference_contact" not in self.columns:
            self._set_dtr_targets(
                {
                    "reference_contact": self.probe.probe_model.contacts_table,
                }
            )
        super().add_row(**kwargs)


extracellular_series_init_dv = [dv for dv in get_docval(AutoExtracellularSeries.__init__) if dv["name"] != "unit"]


@register_class("ExtracellularSeries", "ndx-extracellular-channels")
class ExtracellularSeries(AutoExtracellularSeries):

    @docval(*extracellular_series_init_dv)
    def __init__(self, **kwargs):
        data_shape = get_data_shape(kwargs["data"], strict_no_data_load=True)
        if data_shape is not None:
            # check that the second dimension of `data` matches the length of `channels`
            channels_length = len(kwargs["channels"].data)
            if data_shape[1] != channels_length:
                if data_shape[0] == channels_length:
                    raise ValueError(
                        f"{self.__class__.__name__} '{kwargs['name']}': The length of the second dimension of `data` "
                        f"({data_shape[1]}) does not match the length of `channels` ({channels_length}), "
                        "but instead the length of the first dimension does. `data` is oriented incorrectly and "
                        "should be transposed."
                    )
                else:
                    raise ValueError(
                        f"{self.__class__.__name__} '{kwargs['name']}': The length of the second dimension of `data` "
                        f"({data_shape[1]}) does not match the length of `channels` ({channels_length})."
                    )
            # check that the second dimension of `data` matches the length of `channel_conversion`
            channel_conversion_length = len(kwargs["channel_conversion"])
            if kwargs["channel_conversion"] and data_shape[1] != channel_conversion_length:
                raise ValueError(
                    f"{self.__class__.__name__} '{kwargs['name']}': The length of the second dimension of `data` "
                    f"({data_shape[1]}) does not match the length of `channel_conversion` "
                    f"({channel_conversion_length})."
                )

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
del load_namespaces, get_class, extracellular_series_init_dv, AutoExtracellularSeries
del channels_table_init_dv, AutoChannelsTable
