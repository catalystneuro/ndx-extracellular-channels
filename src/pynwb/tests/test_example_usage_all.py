import datetime
from hdmf.common import DynamicTableRegion
import numpy as np
from pynwb import NWBFile, NWBHDF5IO
import uuid

from ndx_extracellular_channels import (
    ProbeInsertion,
    ContactsTable,
    ProbeModel,
    Probe,
    ChannelsTable,
    ExtracellularSeries,
)


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
    shape="circle",
    contact_id="C1",
    shank_id="shank0",
    plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
    radius_in_um=10.0,
    width_in_um=np.nan,
    height_in_um=np.nan,
    device_channel=1,
)
contacts_table.add_row(
    relative_position_in_mm=[20.0, 10.0],
    shape="square",
    contact_id="C2",
    shank_id="shank0",
    plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
    radius_in_um=np.nan,
    width_in_um=10.0,
    height_in_um=10.0,
    device_channel=2,
)

# add the object into nwbfile.acquisition for testing
# TODO after integration, put this into /general/extracellular_ephys
nwbfile.add_acquisition(contacts_table)

pm = ProbeModel(
    name="Neuropixels 1.0",
    description="A neuropixels probe",
    model="neuropixels 1.0",
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
    depth_in_mm=10.0,  # recommended to provide either `depth_in_mm` or `insertion_position_dv_in_mm`
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
    position_reference = "(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface.",
    position_confirmation_method = "Histology",
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
    print(read_nwbfile.acquisition["ExtracellularSeries"])
    print(read_nwbfile.acquisition["Neuropixels1ChannelsTable"])
    print(read_nwbfile.devices["Neuropixels Probe 1"])
    print(read_nwbfile.devices["Neuropixels 1.0"])
    print(read_nwbfile.acquisition["contacts_table"])
