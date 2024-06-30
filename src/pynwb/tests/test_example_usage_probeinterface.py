import datetime
import ndx_extracellular_channels
import numpy as np
import probeinterface
import pynwb
import uuid


def test_from_probeinterface():

    # following the probeinterface tutorial, create a few probes
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

    polygon = [(-20.0, -30.0), (20.0, -110.0), (60.0, -30.0), (60.0, 190.0), (-20.0, 190.0)]
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

    # create a probe group containing probe2 and probe3
    probegroup = probeinterface.ProbeGroup()
    probegroup.add_probe(probe2)
    probegroup.add_probe(probe3)

    # from_probeinterface always returns a list of ndx_extracellular_channels.Probe devices
    ndx_probes = list()
    model0 = ndx_extracellular_channels.from_probeinterface(probe0)
    ndx_probes.extend(model0)
    model1 = ndx_extracellular_channels.from_probeinterface(probe1, name="probe1")  # override name of probe
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
        assert set(nwbfile.devices.keys()) == {
            "probe0",
            "probe1",
            "probe2",
            "probe3",
            "a1x32-edge-5mm-20-177_H32",
            "Dummy Neuropixels 1.0",
            "Dummy Neuropixels 2.0",
            "Dummy Neuropixels 3.0",
        }
        for device in nwbfile.devices.values():
            assert isinstance(device, (ndx_extracellular_channels.ProbeModel, ndx_extracellular_channels.Probe))
        assert isinstance(nwbfile.devices["probe0"], ndx_extracellular_channels.Probe)
        assert isinstance(nwbfile.devices["probe1"], ndx_extracellular_channels.Probe)
        assert isinstance(nwbfile.devices["probe2"], ndx_extracellular_channels.Probe)
        assert isinstance(nwbfile.devices["probe3"], ndx_extracellular_channels.Probe)
        assert isinstance(nwbfile.devices["a1x32-edge-5mm-20-177_H32"], ndx_extracellular_channels.ProbeModel)
        assert isinstance(nwbfile.devices["Dummy Neuropixels 1.0"], ndx_extracellular_channels.ProbeModel)
        assert isinstance(nwbfile.devices["Dummy Neuropixels 2.0"], ndx_extracellular_channels.ProbeModel)
        assert isinstance(nwbfile.devices["Dummy Neuropixels 3.0"], ndx_extracellular_channels.ProbeModel)

        assert nwbfile.devices["probe0"].name == "probe0"
        assert nwbfile.devices["probe0"].identifier == "0123"
        assert nwbfile.devices["probe0"].probe_model.name == "a1x32-edge-5mm-20-177_H32"
        assert nwbfile.devices["probe0"].probe_model.manufacturer == "Neuronexus"
        assert nwbfile.devices["probe0"].probe_model.ndim == 2
        assert np.all(nwbfile.devices["probe0"].probe_model.planar_contour_in_um == polygon)
        assert np.allclose(nwbfile.devices["probe0"].probe_model.contacts_table.relative_position_in_mm, positions)
        assert np.all(nwbfile.devices["probe0"].probe_model.contacts_table["shape"].data[:] == "circle")
        assert np.all(nwbfile.devices["probe0"].probe_model.contacts_table["radius_in_um"].data[:] == 5.0)

        assert nwbfile.devices["probe1"].name == "probe1"
        assert nwbfile.devices["probe1"].identifier == "1000"
        assert nwbfile.devices["probe1"].probe_model.name == "Dummy Neuropixels 1.0"
        assert nwbfile.devices["probe1"].probe_model.manufacturer == "IMEC"
        assert nwbfile.devices["probe1"].probe_model.ndim == 2
        assert np.allclose(nwbfile.devices["probe1"].probe_model.planar_contour_in_um, probe1.probe_planar_contour)
        assert np.allclose(
            nwbfile.devices["probe1"].probe_model.contacts_table.relative_position_in_mm, probe1.contact_positions
        )
        assert np.all(nwbfile.devices["probe1"].probe_model.contacts_table["shape"].data[:] == "circle")
        assert np.all(
            nwbfile.devices["probe1"].probe_model.contacts_table["radius_in_um"].data[:] == probe1.to_numpy()["radius"]
        )

        assert nwbfile.devices["probe2"].name == "probe2"
        assert nwbfile.devices["probe2"].identifier == "1001"
        assert nwbfile.devices["probe2"].probe_model.name == "Dummy Neuropixels 2.0"
        assert nwbfile.devices["probe2"].probe_model.manufacturer == "IMEC"
        assert nwbfile.devices["probe2"].probe_model.ndim == 2
        assert np.allclose(nwbfile.devices["probe2"].probe_model.planar_contour_in_um, probe2.probe_planar_contour)
        assert np.allclose(
            nwbfile.devices["probe2"].probe_model.contacts_table.relative_position_in_mm, probe2.contact_positions
        )
        assert np.all(nwbfile.devices["probe2"].probe_model.contacts_table["shape"].data[:] == "square")
        assert np.all(
            nwbfile.devices["probe2"].probe_model.contacts_table["width_in_um"].data[:] == probe2.to_numpy()["width"]
        )

        assert nwbfile.devices["probe3"].name == "probe3"
        assert nwbfile.devices["probe3"].identifier == "1002"
        assert nwbfile.devices["probe3"].probe_model.name == "Dummy Neuropixels 3.0"
        assert nwbfile.devices["probe3"].probe_model.manufacturer == "IMEC"
        assert nwbfile.devices["probe3"].probe_model.ndim == 2
        assert np.allclose(nwbfile.devices["probe3"].probe_model.planar_contour_in_um, probe3.probe_planar_contour)
        assert np.allclose(
            nwbfile.devices["probe3"].probe_model.contacts_table.relative_position_in_mm, probe3.contact_positions
        )
        assert np.all(nwbfile.devices["probe3"].probe_model.contacts_table["shape"].data[:] == "circle")
        assert np.all(
            nwbfile.devices["probe3"].probe_model.contacts_table["radius_in_um"].data[:] == probe3.to_numpy()["radius"]
        )

        # for device in nwbfile.devices.values():
        #     print("-------------------")
        #     print(device)
        #     if isinstance(device, ndx_extracellular_channels.ProbeModel):
        #         print(device.name)
        #         print(device.manufacturer)
        #         print(device.ndim)
        #         print(device.planar_contour_in_um)
        #         print(device.contacts_table.to_dataframe())
        #     if isinstance(device, ndx_extracellular_channels.Probe):
        #         pi_probe = ndx_extracellular_channels.to_probeinterface(device)
        #         print(pi_probe)

    # TODO add more tests for other probeinterface IO functions
