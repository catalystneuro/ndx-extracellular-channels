import ndx_extracellular_channels
import numpy as np
import probeinterface
from typing import Union, List
import warnings

# map from probeinterface units to ndx-extracellular-channels units
unit_map = {
    "um": "micrometers",
    "mm": "millimeters",
    "m": "meters",
}
inverted_unit_map = {v: k for k, v in unit_map.items()}


def from_probeinterface(
        probe_or_probegroup: Union[probeinterface.Probe, probeinterface.ProbeGroup],
        name: Union[str, list] = None,
) -> List[ndx_extracellular_channels.Probe]:
    """
    Construct ndx-extracellular-channels Probe objects from a probeinterface.Probe or probeinterface.ProbeGroup.

    Parameters
    ----------
    probe_or_probegroup: Probe or ProbeGroup
        Probe or ProbeGroup to convert to ndx-extracellular-channels ProbeModel devices.
    name: str or list, optional
        Name of the Probe. If a ProbeGroup is passed, this can be a list of names.
        If None, an error will be raised if the Probe(s) does not have a name.

    Returns
    -------
    probe_models: list
        The list of ndx-extracellular-channels Probe objects.
    """
    assert isinstance(probe_or_probegroup, (probeinterface.Probe, probeinterface.ProbeGroup)), \
        f"The input must be a Probe or ProbeGroup, not {type(probe_or_probegroup)}."
    if isinstance(probe_or_probegroup, probeinterface.Probe):
        probes = [probe_or_probegroup]
    else:
        probes = probe_or_probegroup.probes
    if name is not None:
        if isinstance(name, str):
            names = [name]
        else:
            names = name
        assert len(probes) == len(names), "The number of names must match the number of probes."
    else:
        names = [None] * len(probes)

    ndx_probe_models = []
    for probe, name in zip(probes, names):
        ndx_probe_models.append(_single_probe_to_ndx_probe(probe, name))
    return ndx_probe_models


def to_probeinterface(ndx_probe: ndx_extracellular_channels.Probe) -> probeinterface.Probe:
    """
    Construct a probeinterface.Probe from a ndx_extracellular_channels.Probe

    Parameters
    ----------
    ndx_probe: ndx_extracellular_channels.Probe
        ndx_extracellular_channels.Probe to convert to probeinterface.Probe

    Returns
    -------
    Probe: probeinterface.Probe
    """
    positions = []
    shapes = []

    contact_ids = None
    shape_params = None
    shank_ids = None
    plane_axes = None
    device_channel_indices = None

    possible_shape_keys = ["radius", "width", "height"]
    contacts_table = ndx_probe.probe_model.contacts_table

    positions.append(contacts_table["relative_position_in_mm"][:])
    shapes.append(contacts_table["shape"][:])
    if "contact_id" in contacts_table.colnames:
        if contact_ids is None:
            contact_ids = []
        contact_ids.append(contacts_table["contact_id"][:])
    if "device_channel_index_pi" in contacts_table.colnames:
        if device_channel_indices is None:
            device_channel_indices = []
        device_channel_indices.append(contacts_table["device_channel_index_pi"][:])
    if "plane_axes" in contacts_table.colnames:
        if plane_axes is None:
            plane_axes = []
        plane_axes.append(contacts_table["plane_axes"][:])
    if "shank_id" in contacts_table.colnames:
        if shank_ids is None:
            shank_ids = []
        shank_ids.append(contacts_table["shank_id"][:])
    for possible_shape_key in possible_shape_keys:
        if possible_shape_key in contacts_table.colnames:
            if shape_params is None:
                shape_params = []
            shape_params.append([{possible_shape_key: val} for val in contacts_table[possible_shape_key][:]])

    positions = [item for sublist in positions for item in sublist]
    shapes = [item for sublist in shapes for item in sublist]

    if contact_ids is not None:
        contact_ids = [item for sublist in contact_ids for item in sublist]
    if plane_axes is not None:
        plane_axes = [item for sublist in plane_axes for item in sublist]
    if shape_params is not None:
        shape_params = [item for sublist in shape_params for item in sublist]
    if shank_ids is not None:
        shank_ids = [item for sublist in shank_ids for item in sublist]
    if device_channel_indices is not None:
        device_channel_indices = [item for sublist in device_channel_indices for item in sublist]

    probeinterface_probe = probeinterface.Probe(
        ndim=ndx_probe.probe_model.ndim,
        si_units="um",
        name=ndx_probe.name,
        serial_number=ndx_probe.identifier,
        model_name=ndx_probe.probe_model.name,
        manufacturer=ndx_probe.probe_model.manufacturer,
    )
    probeinterface_probe.set_contacts(
        positions=positions, shapes=shapes, shape_params=shape_params, plane_axes=plane_axes, shank_ids=shank_ids
    )
    if contact_ids is not None:
        probeinterface_probe.set_contact_ids(contact_ids=contact_ids)
    if device_channel_indices is not None:
        probeinterface_probe.set_device_channel_indices(channel_indices=device_channel_indices)
    probeinterface_probe.set_planar_contour(ndx_probe.probe_model.planar_contour_in_um)

    return probeinterface_probe


def _single_probe_to_ndx_probe(
        probe: probeinterface.Probe,
        name: Union[str, None] = None
) -> ndx_extracellular_channels.Probe:
    contacts_arr = probe.to_numpy()

    if probe.si_units == "um":
        conversion_factor = 1
    elif probe.si_units == "mm":
        conversion_factor = 1e3
    elif probe.si_units == "m":
        conversion_factor = 1e6

    shape_keys = []
    for shape_params in probe.contact_shape_params:
        keys = list(shape_params.keys())
        for k in keys:
            if k not in shape_keys:
                shape_keys.append(k)


    contacts_table = ndx_extracellular_channels.ContactsTable(
        description="Contacts Table, populated by ProbeInterface",
    )

    for index in np.arange(probe.get_contact_count()):
        kwargs = dict(
            relative_position_in_mm=probe.contact_positions[index],
            plane_axes=probe.contact_plane_axes[index],
            shape=contacts_arr["contact_shapes"][index],
        )
        for k in shape_keys:
            kwargs[f"{k}_in_um"] = contacts_arr[k][index] * conversion_factor
        if probe.contact_ids is not None:
            kwargs["contact_id"] = probe.contact_ids[index]
        if probe.device_channel_indices is not None:
            kwargs["device_channel_index_pi"] = probe.device_channel_indices[index]
        if probe.shank_ids is not None:
            kwargs["shank_id"] = probe.shank_ids[index]
        contacts_table.add_row(kwargs)

    model_name = probe.model_name
    if model_name is None:
        warnings.warn("Probe model name not found in probe annotations, setting to 'unknown'", UserWarning)
        model_name = "unknown"

    probe_model = ndx_extracellular_channels.ProbeModel(
        name=model_name,
        manufacturer=probe.manufacturer,
        ndim=probe.ndim,
        planar_contour_in_um=probe.probe_planar_contour * conversion_factor,
        contacts_table=contacts_table,
    )

    if name is None:
        name = probe.name
        if name is None:
            raise ValueError("Probe name not provided and not found in probe annotations. Please provide a name.")

    probe = ndx_extracellular_channels.Probe(
        name=name,
        probe_model=probe_model,
        identifier=probe.serial_number,
    )

    return probe