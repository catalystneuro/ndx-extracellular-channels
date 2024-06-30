# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import (
    NWBNamespaceBuilder,
    export_spec,
    NWBGroupSpec,
    NWBAttributeSpec,
    NWBDatasetSpec,
    NWBLinkSpec,
)


def main():
    ns_builder = NWBNamespaceBuilder(
        name="""ndx-extracellular-channels""",
        version="""0.1.0""",
        doc="""NWB extension for storing extracellular probe and channels metadata""",
        author=[
            "Alessio Buccino",
            "Kyu Hyun Lee",
            "Ramon Heberto Mayorquin",
            "Cody Baker",
            "Matt Avaylon",
            "Ryan Ly",
            "Ben Dichter",
            "Oliver Ruebel",
            "Geeling Chau",
        ],
        contact=[
            "alessio.buccino@alleninstitute.org",
            "kyuhyun.lee@ucsf.edu",
            "ramon.mayorquin@catalystneuro.com",
            "cody.baker@catalystneuro.com",
            "mavaylon@lbl.gov",
            "rly@lbl.gov",
            "ben.dichter@catalystneuro.com",
            "oruebel@lbl.gov",
            "gchau@caltech.edu",
        ],
    )
    ns_builder.include_namespace("core")

    contacts_table = NWBGroupSpec(
        neurodata_type_def="ContactsTable",
        neurodata_type_inc="DynamicTable",
        doc="Metadata about the contacts of a probe, compatible with the ProbeInterface specification.",
        default_name="contacts_table",
        datasets=[
            NWBDatasetSpec(
                name="relative_position_in_mm",
                neurodata_type_inc="VectorData",
                doc="Relative position of the contact in millimeters, relative to `reference`.",
                dtype="float",
                dims=[["num_contacts", "x, y"], ["num_contacts", "x, y, z"]],
                shape=[[None, 2], [None, 3]],
                attributes=[
                    NWBAttributeSpec(
                        name="reference",
                        doc=(
                            "Reference point for the relative position coordinates and information about the "
                            "coordinate system used, e.g., which direction is positive in the x direction "
                            "(first element), which direction is positive in the y direction (second element), etc."
                        ),
                        dtype="text",
                        required=False,  # TODO should this be required?
                    )
                ],
            ),
            NWBDatasetSpec(
                name="contact_id",  # id is already used by DynamicTable
                neurodata_type_inc="VectorData",
                doc="Unique ID of the contact",
                dtype="text",
                quantity="?",
            ),
            NWBDatasetSpec(
                # NOTE: cannot end this name with "_index" because it conflicts with ragged arrays
                name="device_channel",
                neurodata_type_inc="VectorData",
                doc=(
                    "Index of the channel connected to the contact on the device. "
                    "Probes can have a complex contact indexing system due to the probe layout. "
                    "When they are plugged into a recording device like an Open Ephys with an Intan headstage, "
                    "the channel order can be mixed again. So the physical contact channel index "
                    "is rarely the channel index on the device. See the probeinterface tutorial on automatic "
                    "wiring for an example: "
                    "https://probeinterface.readthedocs.io/en/main/examples/ex_11_automatic_wiring.html#sphx-glr-examples-ex-11-automatic-wiring-py"
                ),
                dtype="int",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="shank_id",
                neurodata_type_inc="VectorData",
                doc="Shank ID of the contact",
                dtype="text",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="plane_axes",
                neurodata_type_inc="VectorData",
                doc=(
                    "The axes defining the contact plane. "
                    "See 'contact_plane_axes' in "
                    "https://probeinterface.readthedocs.io/en/main/format_spec.html for more details."
                ),
                dtype="float",
                dims=[["num_contacts", "v1, v2", "x, y"], ["num_contacts", "v1, v2", "x, y, z"]],
                shape=[[None, 2, 2], [None, 2, 3]],
                quantity="?",
            ),
            NWBDatasetSpec(
                name="shape",
                neurodata_type_inc="VectorData",
                doc="Shape of the contact; e.g. 'circle'",
                dtype="text",
            ),
            NWBDatasetSpec(
                name="radius_in_um",
                neurodata_type_inc="VectorData",
                doc="Radius of a circular contact, in micrometers.",
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="width_in_um",
                neurodata_type_inc="VectorData",
                doc="Width of a rectangular or square contact, in micrometers.",
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="height_in_um",
                neurodata_type_inc="VectorData",
                doc="Height of a rectangular contact, in micrometers.",
                dtype="float",
                quantity="?",
            ),
        ],
    )

    probe = NWBGroupSpec(
        neurodata_type_def="Probe",
        neurodata_type_inc="Device",
        doc="Specific instance of a neural probe object.",
        links=[
            NWBLinkSpec(
                name="probe_model",
                doc="The model of the probe used to record the data.",
                target_type="ProbeModel",
            ),
        ],
        attributes=[
            NWBAttributeSpec(
                name="identifier",
                doc="Identifier of the probe, usually the serial number.",
                dtype="text",
                required=False,
            ),
        ],
    )

    probe_model = NWBGroupSpec(
        neurodata_type_def="ProbeModel",
        neurodata_type_inc="Device",
        doc=(
            "Neural probe object, compatible with the ProbeInterface specification. The name of the object should "
            'be the model name of the probe, e.g., "Neuropixels 1.0".'
        ),
        groups=[
            NWBGroupSpec(
                name="contacts_table",
                neurodata_type_inc="ContactsTable",
                doc="Neural probe contacts, compatible with the ProbeInterface specification",
            ),
        ],
        attributes=[
            # inherits name, description, manufacturer from Device
            NWBAttributeSpec(name="ndim", doc="dimension of the probe", dtype="int", default_value=2),
            NWBAttributeSpec(
                # although the ProbeModel also has a name attribute, the name must be unique across all
                # devices in the NWB file, and users may decide to use a more descriptive name than just
                # the model name
                name="model",
                doc='Name of the model of the probe, e.g., "Neuropixels 1.0".',
                dtype="text",
            ),
            NWBAttributeSpec(
                name="planar_contour_in_um",  # TODO should this just be "contour"?
                doc=(
                    "The coordinates of the nodes of the polygon that describe the shape (contour) of the probe, "
                    "in micrometers. The first and last points are connected to close the polygon. "
                    "e.g., [(-20., -30.), (20., -110.), (60., -30.), (60., 190.), (-20., 190.)]."
                    "See 'probe_planar_contour' in "
                    "https://probeinterface.readthedocs.io/en/main/format_spec.html for more details."
                ),
                dtype="float",
                dims=[["num_points", "x, y"], ["num_points", "x, y, z"]],
                shape=[[None, 2], [None, 3]],
                required=False,
            ),
        ],
    )

    probe_insertion = NWBGroupSpec(
        neurodata_type_def="ProbeInsertion",
        neurodata_type_inc="NWBContainer",
        doc=(
            "Metadata about the insertion of a probe into the brain, which can be used to determine the location of "
            "the probe in the brain."
        ),
        default_name="probe_insertion",
        attributes=[
            # TODO waiting on https://github.com/hdmf-dev/hdmf/issues/1099 to add these attributes
            NWBAttributeSpec(
                name="insertion_position_ap_in_mm",
                doc=(
                    "Anteroposterior (AP) stereotactic coordinate of where the probe was inserted, in millimeters. "
                    "+ is anterior. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                required=False,
            ),
            NWBAttributeSpec(
                name="insertion_position_ml_in_mm",
                doc=(
                    "Mediolateral (ML) stereotactic coordinate of where the probe was inserted, in millimeters. "
                    "+ is right. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                required=False,
            ),
            NWBAttributeSpec(
                name="insertion_position_dv_in_mm",
                doc=(
                    "Dorsoventral (DV) stereotactic coordinate of where the probe was inserted, in millimeters. "
                    "+ is up. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                required=False,
            ),
            NWBAttributeSpec(
                name="depth_in_mm",
                doc=(
                    "Depth that the probe was driven along `insertion_angle` starting from "
                    "`insertion_position_ap_in_mm` and `insertion_position_ml_in_mm`, in millimeters. This is an "
                    "alternate method of providing the dorsal-ventral coordinate of the probe insertion site. If "
                    "both `insertion_position_dv_in_mm` and `depth_in_mm` are provided, the values should be "
                    "consistent."
                ),
                dtype="float",
                required=False,
            ),
            NWBAttributeSpec(
                name="position_reference",
                doc=(
                    "Location of the origin (0, 0, 0) for `insertion_position_{X}_in_mm` coordinates, e.g., "
                    '"(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface".'
                ),
                dtype="text",
                required=False,
            ),
            NWBAttributeSpec(
                name="hemisphere",  # TODO this is useful to cache but could be done at the API level
                doc=(
                    'The hemisphere ("left" or "right") of the targeted location of the optogenetic stimulus site. '
                    "Should be consistent with `insertion_position_in_mm.ml` coordinate (left = ml < 0, "
                    "right = ml > 0)."
                ),
                dtype="text",
                required=False,
            ),
            NWBAttributeSpec(
                name="insertion_angle_pitch_in_deg",
                doc=(
                    "The pitch angle of the probe at the time of insertion, in degrees. "
                    "Pitch = rotation around left-right axis, like nodding (+ is rotating the nose upward). "
                    "Zero is defined as the probe being parallel to an axial slice of the brain."
                    "Yaw = rotation around dorsal-ventral axis, like shaking (+ is rotating the nose rightward). "
                    "Roll = rotation around anterior-posterior axis, like tilting (+ is rotating the right side "
                    "downward)."
                ),
                dtype="float",
                required=False,
            ),
            NWBAttributeSpec(
                name="insertion_angle_yaw_in_deg",
                doc=(
                    "The yaw angle of the probe at the time of insertion, in degrees. "
                    "Yaw = rotation around dorsal-ventral axis, like shaking (+ is rotating the nose rightward). "
                    "Zero is defined as the probe being parallel to an sagittal slice of the brain."
                ),
                dtype="float",
                required=False,
            ),
            NWBAttributeSpec(
                name="insertion_angle_roll_in_deg",
                doc=(
                    "The roll angle of the probe at the time of insertion, in degrees. "
                    "Roll = rotation around anterior-posterior axis, like tilting (+ is rotating the right side "
                    "downward). Zero is defined as the probe being parallel to a coronal slice of the brain. "
                ),
                dtype="float",
                required=False,
            ),
        ],
    )

    channels_table = NWBGroupSpec(
        neurodata_type_def="ChannelsTable",
        neurodata_type_inc="DynamicTable",
        doc="Metadata about the channels used in an extracellular recording from a single probe.",
        default_name="ChannelsTable",
        groups=[
            NWBGroupSpec(
                name="probe_insertion",
                neurodata_type_inc="ProbeInsertion",
                doc="Information about the insertion of a probe into the brain.",
                quantity="?",
            ),
        ],
        datasets=[
            NWBDatasetSpec(
                name="contact",
                neurodata_type_inc="DynamicTableRegion",
                doc="The row in a ContactsTable that represents the contact used as a channel.",
                quantity="?",  # TODO should this be optional?
            ),
            NWBDatasetSpec(
                name="reference_contact",
                neurodata_type_inc="DynamicTableRegion",
                doc="The row in a ContactsTable that represents the contact used as a reference.",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="filter",
                neurodata_type_inc="VectorData",
                dtype="text",
                doc=(
                    "The filter used on the raw (wideband) voltage data from this contact, including the filter "
                    'name and frequency cutoffs, e.g., "High-pass filter at 300 Hz."'
                ),
                quantity="?",
            ),
            NWBDatasetSpec(
                name="estimated_position_ap_in_mm",
                neurodata_type_inc="VectorData",
                doc=(
                    "Anteroposterior (AP) stereotactic coordinate of the estimated contact position, in millimeters. "
                    "+ is anterior. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="estimated_position_ml_in_mm",
                neurodata_type_inc="VectorData",
                doc=(
                    "Mediolateral (ML) stereotactic coordinate of the estimated contact position, in millimeters. "
                    "+ is right. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="estimated_position_dv_in_mm",
                neurodata_type_inc="VectorData",
                doc=(
                    "Dorsoventral (DV) stereotactic coordinate of the estimated contact position, in millimeters. "
                    "+ is up. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="estimated_brain_area",
                neurodata_type_inc="VectorData",
                dtype="text",
                doc=('The brain area of the estimated contact position, e.g., "CA1".'),
                quantity="?",
            ),
            NWBDatasetSpec(
                name="confirmed_position_ap_in_mm",
                neurodata_type_inc="VectorData",
                doc=(
                    "Anteroposterior (AP) stereotactic coordinate of the confirmed contact position, in millimeters. "
                    "+ is anterior. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="confirmed_position_ml_in_mm",
                neurodata_type_inc="VectorData",
                doc=(
                    "Mediolateral (ML) stereotactic coordinate of the confirmed contact position, in millimeters. "
                    "+ is right. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="confirmed_position_dv_in_mm",
                neurodata_type_inc="VectorData",
                doc=(
                    "Dorsoventral (DV) stereotactic coordinate of the confirmed contact position, in millimeters. "
                    "+ is up. Coordinate is relative to the zero-point described in `position_reference`."
                ),
                dtype="float",
                quantity="?",
            ),
            NWBDatasetSpec(
                name="confirmed_brain_area",
                neurodata_type_inc="VectorData",
                dtype="text",
                doc=('The brain area of the actual contact position, e.g., "CA1".'),
                quantity="?",
            ),
        ],
        links=[
            NWBLinkSpec(
                name="probe",
                doc="The probe that the channels belongs to.",
                target_type="Probe",
            ),
        ],
        attributes=[
            NWBAttributeSpec(
                name="position_reference",
                doc=(
                    "Location of the origin (0, 0, 0) for `{X}_position_{Y}_in_mm` coordinates, e.g., "
                    '"(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface".'
                ),
                dtype="text",
                required=False,
            ),
            NWBAttributeSpec(
                name="reference_mode",
                doc=(
                    'The reference mode used for the recording; e.g., "external wire in CSF", '
                    'common reference", "skull screw over frontal cortex".'
                ),
                dtype="text",
                required=False,
            ),
            NWBAttributeSpec(
                name="position_confirmation_method",
                doc=(
                    "Description of the method used to confirm the position of the contacts or brain area, "
                    'e.g., "histology", "MRI".'
                ),
                dtype="text",
                required=False,
            ),
        ],
    )

    extracellular_series = NWBGroupSpec(
        neurodata_type_def="ExtracellularSeries",
        neurodata_type_inc="TimeSeries",
        doc=(
            "Extracellular recordings from a single probe. Create multiple instances of this class for different "
            "probes."
        ),
        datasets=[
            NWBDatasetSpec(
                name="data",
                doc="Recorded voltage data.",
                dtype="numeric",
                shape=[None, None],
                dims=["num_times", "num_channels"],
                attributes=[
                    NWBAttributeSpec(
                        name="unit",
                        doc=(
                            "Base unit of measurement for working with the data. This value is fixed to "
                            "'volts'. Actual stored values are not necessarily stored in these units. To "
                            "access the data in these units, multiply 'data' by 'conversion', followed by "
                            "'channel_conversion' (if present), and then add 'offset'."
                        ),
                        value="volts",
                        dtype="text",
                    )
                ],
            ),
            NWBDatasetSpec(
                name="channels",
                neurodata_type_inc="DynamicTableRegion",
                doc=(
                    "DynamicTableRegion pointer to rows in a ChannelsTable that represent the channels used to "
                    "collect the data in this recording."
                ),
            ),
            NWBDatasetSpec(
                name="channel_conversion",
                dtype="float",
                shape=[None],
                dims=["num_channels"],
                doc=(
                    "Channel-specific conversion factor. Multiply the data in the 'data' dataset by these "
                    "values along the channel axis (as indicated by axis attribute) AND by the global "
                    "conversion factor in the 'conversion' attribute of 'data' to get the data values in "
                    "Volts, i.e, data in Volts = data * data.conversion * channel_conversion. This "
                    "approach allows for both global and per-channel data conversion factors needed "
                    "to support the storage of electrical recordings as native values generated by data "
                    "acquisition systems. If this dataset is not present, then there is no channel-specific "
                    "conversion factor, i.e. it is 1 for all channels."
                ),
                quantity="?",
                attributes=[
                    NWBAttributeSpec(
                        name="axis",
                        dtype="int",
                        doc=(
                            "The zero-indexed axis of the 'data' dataset that the channel-specific conversion"
                            "factor applies to. This value is fixed to 1."
                        ),
                        value=1,
                    )
                ],
            ),
        ],
    )

    new_data_types = [contacts_table, probe_model, probe, probe_insertion, channels_table, extracellular_series]

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
