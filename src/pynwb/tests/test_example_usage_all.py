import datetime
import uuid

import numpy as np
from hdmf.common import DynamicTableRegion
from ndx_extracellular_channels import (
    ChannelsTable,
    ContactsTable,
    ExtracellularSeries,
    Probe,
    ProbeInsertion,
    ProbeModel,
)

from pynwb import NWBHDF5IO, NWBFile


def test_all_classes():

    # initialize an NWBFile object
    nwbfile = NWBFile(
        session_description="A description of my session",
        identifier=str(uuid.uuid4()),
        session_start_time=datetime.datetime.now(datetime.timezone.utc),
    )

    contacts_table = ContactsTable(
        description="Test contacts table",
    )
    # for demonstration, mix and match different shapes. np.nan means the radius/width/height does not apply
    contacts_table.add_row(
        relative_position_in_mm=[10.0, 10.0],
        contact_id="C1",
        device_channel=1,
        shank_id="shank0",
        plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
        shape="circle",
        radius_in_um=10.0,
        width_in_um=np.nan,
        height_in_um=np.nan,
    )
    contacts_table.add_row(
        relative_position_in_mm=[20.0, 10.0],
        contact_id="C2",
        device_channel=2,
        shank_id="shank0",
        plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
        shape="square",
        radius_in_um=np.nan,
        width_in_um=10.0,
        height_in_um=10.0,
    )

    # add the object into nwbfile.acquisition for testing
    # TODO after integration, put this into /general/extracellular_ephys
    nwbfile.add_acquisition(contacts_table)

    pm = ProbeModel(
        name="Neuropixels 1.0",
        description="A neuropixels probe",
        model="Neuropixels 1.0",
        manufacturer="IMEC",
        planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
        contacts_table=contacts_table,
    )
    # TODO put this into /general/device_models
    nwbfile.add_device(pm)

    probe = Probe(
        name="Neuropixels Probe 1",
        identifier="28948291",
        probe_model=pm,
    )
    nwbfile.add_device(probe)

    pi = ProbeInsertion(
        position_reference="(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface.",
        hemisphere="left",
        depth_in_mm=10.0,
        insertion_position_ap_in_mm=2.0,
        insertion_position_ml_in_mm=-4.0,
        insertion_angle_roll_in_deg=-10.0,
        insertion_angle_pitch_in_deg=0.0,
        insertion_angle_yaw_in_deg=0.0,
    )

    channels_table = ChannelsTable(
        name="Neuropixels1ChannelsTable",  # test custom name
        description="Test channels table",
        reference_mode="Referenced to channel 2.",
        position_reference="(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface.",
        position_confirmation_method="Histology",
        probe=probe,
        probe_insertion=pi,
        target_tables={
            "contact": probe.probe_model.contacts_table,
            "reference_contact": probe.probe_model.contacts_table,
        },
        # TODO should not need to specify the above
    )

    # all of the keyword arguments in add_row are optional
    channels_table.add_row(
        contact=0,
        reference_contact=2,
        filter="High-pass at 300 Hz",
        estimated_position_ap_in_mm=2.0,
        estimated_position_ml_in_mm=-5.0,
        estimated_position_dv_in_mm=-9.5,
        estimated_brain_area="CA3",
        confirmed_position_ap_in_mm=2.0,
        confirmed_position_ml_in_mm=-4.9,
        confirmed_position_dv_in_mm=-9.5,
        confirmed_brain_area="CA3",
    )
    channels_table.add_row(
        contact=1,
        reference_contact=2,
        filter="High-pass at 300 Hz",
        estimated_position_ap_in_mm=2.0,
        estimated_position_ml_in_mm=-4.9,
        estimated_position_dv_in_mm=-9.3,
        estimated_brain_area="CA3",
        confirmed_position_ap_in_mm=2.0,
        confirmed_position_ml_in_mm=-4.8,
        confirmed_position_dv_in_mm=-9.3,
        confirmed_brain_area="CA3",
    )

    # put this in nwbfile.acquisition for testing
    nwbfile.add_acquisition(channels_table)

    channels = DynamicTableRegion(
        name="channels",  # NOTE: this must be named "channels" when used in ExtracellularSeries
        data=[0, 1, 2],
        description="All of the channels",
        table=channels_table,
    )

    es = ExtracellularSeries(
        name="ExtracellularSeries",
        data=[0.0, 1.0, 2.0],
        timestamps=[0.0, 0.001, 0.0002],
        channels=channels,
        channel_conversion=[1.0, 1.1, 1.2],
        conversion=1e5,
        offset=0.001,
        unit="volts",  # TODO should not have to specify this in init
    )

    nwbfile.add_acquisition(es)

    # write the NWBFile to disk
    path = "test_extracellular_channels.nwb"
    with NWBHDF5IO(path, mode="w") as io:
        io.write(nwbfile)

    # read the NWBFile from disk
    with NWBHDF5IO(path, mode="r") as io:
        read_nwbfile = io.read()

        read_eseries = read_nwbfile.acquisition["ExtracellularSeries"]
        read_channels_table = read_nwbfile.acquisition["Neuropixels1ChannelsTable"]
        read_contacts_table = read_nwbfile.acquisition["contacts_table"]

        np.testing.assert_array_equal(read_eseries.data[:], [0.0, 1.0, 2.0])
        np.testing.assert_array_equal(read_eseries.timestamps[:], [0.0, 0.001, 0.0002])
        np.testing.assert_array_equal(read_eseries.channels.data[:], [0, 1, 2])
        assert read_eseries.channels.description == "All of the channels"
        assert read_eseries.channels.table is read_channels_table
        np.testing.assert_array_equal(read_eseries.channel_conversion[:], [1.0, 1.1, 1.2])
        assert read_eseries.conversion == 1e5
        assert read_eseries.offset == 0.001
        assert read_eseries.unit == "volts"

        assert read_channels_table.name == "Neuropixels1ChannelsTable"
        assert read_channels_table.description == "Test channels table"
        assert read_channels_table.reference_mode == "Referenced to channel 2."
        assert (
            read_channels_table.position_reference
            == "(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface."
        )
        assert read_channels_table.position_confirmation_method == "Histology"
        assert read_channels_table.probe is read_nwbfile.devices["Neuropixels Probe 1"]
        assert len(read_channels_table) == 2
        assert read_channels_table["contact"].table is read_contacts_table
        np.testing.assert_array_equal(read_channels_table["contact"].data[:], [0, 1])
        assert read_channels_table["reference_contact"].table is read_contacts_table
        np.testing.assert_array_equal(read_channels_table["reference_contact"].data[:], [2, 2])
        np.testing.assert_array_equal(
            read_channels_table["filter"].data[:], ["High-pass at 300 Hz", "High-pass at 300 Hz"]
        )
        np.testing.assert_array_equal(read_channels_table["estimated_position_ap_in_mm"].data[:], [2.0, 2.0])
        np.testing.assert_array_equal(read_channels_table["estimated_position_ml_in_mm"].data[:], [-5.0, -4.9])
        np.testing.assert_array_equal(read_channels_table["estimated_position_dv_in_mm"].data[:], [-9.5, -9.3])
        np.testing.assert_array_equal(read_channels_table["estimated_brain_area"].data[:], ["CA3", "CA3"])
        np.testing.assert_array_equal(read_channels_table["confirmed_position_ap_in_mm"].data[:], [2.0, 2.0])
        np.testing.assert_array_equal(read_channels_table["confirmed_position_ml_in_mm"].data[:], [-4.9, -4.8])
        np.testing.assert_array_equal(read_channels_table["confirmed_position_dv_in_mm"].data[:], [-9.5, -9.3])
        np.testing.assert_array_equal(read_channels_table["confirmed_brain_area"].data[:], ["CA3", "CA3"])

        assert (
            read_channels_table.probe_insertion.position_reference
            == "(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface."
        )
        assert read_channels_table.probe_insertion.hemisphere == "left"
        assert read_channels_table.probe_insertion.depth_in_mm == 10.0
        assert read_channels_table.probe_insertion.insertion_position_ap_in_mm == 2.0
        assert read_channels_table.probe_insertion.insertion_position_ml_in_mm == -4.0
        assert read_channels_table.probe_insertion.insertion_angle_roll_in_deg == -10.0
        assert read_channels_table.probe_insertion.insertion_angle_pitch_in_deg == 0.0
        assert read_channels_table.probe_insertion.insertion_angle_yaw_in_deg == 0.0

        assert read_nwbfile.devices["Neuropixels Probe 1"].name == "Neuropixels Probe 1"
        assert read_nwbfile.devices["Neuropixels Probe 1"].identifier == "28948291"
        assert read_nwbfile.devices["Neuropixels Probe 1"].probe_model is read_nwbfile.devices["Neuropixels 1.0"]

        assert read_nwbfile.devices["Neuropixels 1.0"].name == "Neuropixels 1.0"
        assert read_nwbfile.devices["Neuropixels 1.0"].description == "A neuropixels probe"
        assert read_nwbfile.devices["Neuropixels 1.0"].model == "Neuropixels 1.0"
        assert read_nwbfile.devices["Neuropixels 1.0"].manufacturer == "IMEC"
        np.testing.assert_array_equal(
            read_nwbfile.devices["Neuropixels 1.0"].planar_contour_in_um,
            [[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
        )
        assert read_nwbfile.devices["Neuropixels 1.0"].contacts_table is read_contacts_table

        assert read_contacts_table.name == "contacts_table"
        assert read_contacts_table.description == "Test contacts table"
        np.testing.assert_array_equal(
            read_contacts_table["relative_position_in_mm"].data[:], [[10.0, 10.0], [20.0, 10.0]]
        )
        np.testing.assert_array_equal(read_contacts_table["shape"].data[:], ["circle", "square"])
        np.testing.assert_array_equal(read_contacts_table["contact_id"].data[:], ["C1", "C2"])
        np.testing.assert_array_equal(read_contacts_table["shank_id"].data[:], ["shank0", "shank0"])
        np.testing.assert_array_equal(
            read_contacts_table["plane_axes"].data[:], [[[0.0, 1.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 0.0]]]
        )
        np.testing.assert_array_equal(read_contacts_table["radius_in_um"].data[:], [10.0, np.nan])
        np.testing.assert_array_equal(read_contacts_table["width_in_um"].data[:], [np.nan, 10.0])
        np.testing.assert_array_equal(read_contacts_table["height_in_um"].data[:], [np.nan, 10.0])
        np.testing.assert_array_equal(read_contacts_table["device_channel"].data[:], [1, 2])
