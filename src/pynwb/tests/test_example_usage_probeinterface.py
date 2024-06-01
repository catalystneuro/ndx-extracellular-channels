import datetime
import ndx_extracellular_channels
import numpy as np
import probeinterface
import pynwb
import uuid

# following the probeinterface tutorial
n = 24
positions = np.zeros((n, 2))
for i in range(n):
    x = i // 8
    y = i % 8
    positions[i] = x, y
positions *= 20
positions[8:16, 1] -= 10

probe0 = probeinterface.Probe(
    ndim=2,
    si_units="um",
    name="probe0",
    serial_number="0123",
    model_name="a1x32-edge-5mm-20-177_H32",
    manufacturer="Neuronexus",
)
probe0.set_contacts(positions=positions, shapes="circle", shape_params={"radius": 5})

polygon = [(-20., -30.), (20., -110.), (60., -30.), (60., 190.), (-20., 190.)]
probe0.set_planar_contour(polygon)

probe1 = probeinterface.generate_dummy_probe(elec_shapes="circle")
probe1.serial_number = "1000"
probe1.model_name = "Dummy Neuropixels 1.0"
probe1.manufacturer = "IMEC"
probe1.move([250, -90])

probe2 = probeinterface.generate_dummy_probe(elec_shapes="square")
probe2.name = "probe2"
probe2.serial_number = "1001"
probe2.model_name = "Dummy Neuropixels 2.0"
probe2.manufacturer = "IMEC"
probe2.move([500, -90])

probe3 = probeinterface.generate_dummy_probe(elec_shapes="circle")
probe3.serial_number = "1002"
probe3.model_name = "Dummy Neuropixels 3.0"
probe3.manufacturer = "IMEC"
probe3.move([750, -90])

probegroup = probeinterface.ProbeGroup()
probegroup.add_probe(probe2)
probegroup.add_probe(probe3)

# from_probeinterface always returns a list of ndx_extracellular_channels.Probe devices
ndx_probes = list()
model0 = ndx_extracellular_channels.from_probeinterface(probe0)
ndx_probes.extend(model0)
model1 = ndx_extracellular_channels.from_probeinterface(probe1, name="probe1")  # override name
ndx_probes.extend(model1)
group_probes = ndx_extracellular_channels.from_probeinterface(probegroup, name=[None, "probe3"])
ndx_probes.extend(group_probes)

nwbfile = pynwb.NWBFile(
    session_description="A description of my session",
    identifier=str(uuid.uuid4()),
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)

# add Probe as NWB Devices
for ndx_probe in ndx_probes:
    nwbfile.add_device(ndx_probe.probe_model)
    nwbfile.add_device(ndx_probe)

with pynwb.NWBHDF5IO("test_probeinterface.nwb", "w") as io:
    io.write(nwbfile)

# read the file and check the content
with pynwb.NWBHDF5IO("test_probeinterface.nwb", "r", load_namespaces=True) as io:
    nwbfile = io.read()
    for device in nwbfile.devices.values():
        print("-------------------")
        print(device)
        if isinstance(device, ndx_extracellular_channels.ProbeModel):
            print(device.name)
            print(device.manufacturer)
            print(device.ndim)
            print(device.planar_contour_in_um)
            print(device.contacts_table.to_dataframe())
        if isinstance(device, ndx_extracellular_channels.Probe):
            pi_probe = ndx_extracellular_channels.to_probeinterface(device)
            print(pi_probe)
