import datetime
import uuid

import ndx_extracellular_channels
import numpy as np
import numpy.testing as npt
import probeinterface

import pynwb


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

    probe1 = probeinterface.generate_dummy_probe(elec_shapes="circle")  # no name set
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
    probe3.name = "probe3"
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
    # override name of probe3
    group_probes = ndx_extracellular_channels.from_probeinterface(probegroup, name=[None, "renamed_probe3"])
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
    with pynwb.NWBHDF5IO("test_probeinterface.nwb", "r") as io:
        nwbfile = io.read()
        assert set(nwbfile.devices.keys()) == {
            "probe0",
            "probe1",
            "probe2",
            "renamed_probe3",
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
        assert isinstance(nwbfile.devices["renamed_probe3"], ndx_extracellular_channels.Probe)
        assert isinstance(nwbfile.devices["a1x32-edge-5mm-20-177_H32"], ndx_extracellular_channels.ProbeModel)
        assert isinstance(nwbfile.devices["Dummy Neuropixels 1.0"], ndx_extracellular_channels.ProbeModel)
        assert isinstance(nwbfile.devices["Dummy Neuropixels 2.0"], ndx_extracellular_channels.ProbeModel)
        assert isinstance(nwbfile.devices["Dummy Neuropixels 3.0"], ndx_extracellular_channels.ProbeModel)

        assert nwbfile.devices["probe0"].name == "probe0"
        assert nwbfile.devices["probe0"].identifier == "0123"
        assert nwbfile.devices["probe0"].probe_model.name == "a1x32-edge-5mm-20-177_H32"
        assert nwbfile.devices["probe0"].probe_model.manufacturer == "Neuronexus"
        assert nwbfile.devices["probe0"].probe_model.ndim == 2
        npt.assert_array_equal(nwbfile.devices["probe0"].probe_model.planar_contour_in_um, polygon)
        npt.assert_allclose(nwbfile.devices["probe0"].probe_model.contacts_table.relative_position_in_mm, positions)
        npt.assert_array_equal(nwbfile.devices["probe0"].probe_model.contacts_table["shape"].data[:], "circle")
        npt.assert_array_equal(nwbfile.devices["probe0"].probe_model.contacts_table["radius_in_um"].data[:], 5.0)

        assert nwbfile.devices["probe1"].name == "probe1"
        assert nwbfile.devices["probe1"].identifier == "1000"
        assert nwbfile.devices["probe1"].probe_model.name == "Dummy Neuropixels 1.0"
        assert nwbfile.devices["probe1"].probe_model.manufacturer == "IMEC"
        assert nwbfile.devices["probe1"].probe_model.ndim == 2
        npt.assert_allclose(nwbfile.devices["probe1"].probe_model.planar_contour_in_um, probe1.probe_planar_contour)
        npt.assert_allclose(
            nwbfile.devices["probe1"].probe_model.contacts_table.relative_position_in_mm, probe1.contact_positions
        )
        npt.assert_array_equal(nwbfile.devices["probe1"].probe_model.contacts_table["shape"].data[:], "circle")
        npt.assert_array_equal(
            nwbfile.devices["probe1"].probe_model.contacts_table["radius_in_um"].data[:], probe1.to_numpy()["radius"]
        )

        assert nwbfile.devices["probe2"].name == "probe2"
        assert nwbfile.devices["probe2"].identifier == "1001"
        assert nwbfile.devices["probe2"].probe_model.name == "Dummy Neuropixels 2.0"
        assert nwbfile.devices["probe2"].probe_model.manufacturer == "IMEC"
        assert nwbfile.devices["probe2"].probe_model.ndim == 2
        npt.assert_allclose(nwbfile.devices["probe2"].probe_model.planar_contour_in_um, probe2.probe_planar_contour)
        npt.assert_allclose(
            nwbfile.devices["probe2"].probe_model.contacts_table.relative_position_in_mm, probe2.contact_positions
        )
        npt.assert_array_equal(nwbfile.devices["probe2"].probe_model.contacts_table["shape"].data[:], "square")
        npt.assert_array_equal(
            nwbfile.devices["probe2"].probe_model.contacts_table["width_in_um"].data[:], probe2.to_numpy()["width"]
        )

        assert nwbfile.devices["renamed_probe3"].name == "renamed_probe3"
        assert nwbfile.devices["renamed_probe3"].identifier == "1002"
        assert nwbfile.devices["renamed_probe3"].probe_model.name == "Dummy Neuropixels 3.0"
        assert nwbfile.devices["renamed_probe3"].probe_model.manufacturer == "IMEC"
        assert nwbfile.devices["renamed_probe3"].probe_model.ndim == 2
        npt.assert_allclose(
            nwbfile.devices["renamed_probe3"].probe_model.planar_contour_in_um, probe3.probe_planar_contour
        )
        npt.assert_allclose(
            nwbfile.devices["renamed_probe3"].probe_model.contacts_table.relative_position_in_mm,
            probe3.contact_positions,
        )
        npt.assert_array_equal(nwbfile.devices["renamed_probe3"].probe_model.contacts_table["shape"].data[:], "circle")
        npt.assert_array_equal(
            nwbfile.devices["renamed_probe3"].probe_model.contacts_table["radius_in_um"].data[:],
            probe3.to_numpy()["radius"],
        )


def test_to_probeinterface():

    # create a NWB file with a few probes
    nwbfile = pynwb.NWBFile(
        session_description="A description of my session",
        identifier=str(uuid.uuid4()),
        session_start_time=datetime.datetime.now(datetime.timezone.utc),
    )

    # create a probe model
    probe_model0 = ndx_extracellular_channels.ProbeModel(
        name="a1x32-edge-5mm-20-177_H32",
        model="a1x32-edge-5mm-20-177_H32",
        manufacturer="Neuronexus",
        ndim=2,
        planar_contour_in_um=[(-20.0, -30.0), (20.0, -110.0), (60.0, -30.0), (60.0, 190.0), (-20.0, 190.0)],
        contacts_table=ndx_extracellular_channels.ContactsTable(
            name="contacts_table",
            description="a table with electrode contacts",
            columns=[
                pynwb.core.VectorData(
                    name="relative_position_in_mm",
                    description="the relative position of the contact in mm",
                    data=[
                        (0.0, 0.0),
                        (0.0, 20.0),
                        (0.0, 40.0),
                        (0.0, 60.0),
                        (0.0, 80.0),
                        (0.0, 100.0),
                        (0.0, 120.0),
                        (0.0, 140.0),
                        (20.0, 0.0),
                        (20.0, 20.0),
                        (20.0, 40.0),
                        (20.0, 60.0),
                        (20.0, 80.0),
                        (20.0, 100.0),
                        (20.0, 120.0),
                        (20.0, 140.0),
                        (40.0, 0.0),
                        (40.0, 20.0),
                        (40.0, 40.0),
                        (40.0, 60.0),
                        (40.0, 80.0),
                        (40.0, 100.0),
                        (40.0, 120.0),
                        (40.0, 140.0),
                    ],
                ),
                pynwb.core.VectorData(
                    name="shape",
                    description="the shape of the contact",
                    data=["circle"] * 24,
                ),
                pynwb.core.VectorData(
                    name="radius_in_um",
                    description="the radius of the contact in um",
                    data=[5.0] * 24,
                ),
            ],
        ),
    )

    # create a probe
    probe0 = ndx_extracellular_channels.Probe(
        name="probe0",
        identifier="0123",
        probe_model=probe_model0,
    )

    pi_probe0 = ndx_extracellular_channels.to_probeinterface(probe0)
    assert pi_probe0.ndim == 2
    assert pi_probe0.si_units == "um"
    assert pi_probe0.name == "probe0"
    assert pi_probe0.serial_number == "0123"
    assert pi_probe0.model_name == "a1x32-edge-5mm-20-177_H32"
    assert pi_probe0.manufacturer == "Neuronexus"
    npt.assert_array_equal(pi_probe0.contact_positions, probe_model0.contacts_table.relative_position_in_mm)
    npt.assert_array_equal(pi_probe0.contact_shapes, "circle")
    npt.assert_array_equal(pi_probe0.to_numpy()["radius"], 5.0)

    ct2 = ndx_extracellular_channels.ContactsTable(
        description="Test contacts table",
    )

    # for testing, mix and match different shapes. np.nan means the radius/width/height does not apply
    ct2.add_row(
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
    ct2.add_row(
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
    probe_model1 = ndx_extracellular_channels.ProbeModel(
        name="Neuropixels 1.0",
        description="A neuropixels probe",
        model="Neuropixels 1.0",
        manufacturer="IMEC",
        planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
        contacts_table=ct2,
    )

    # create a probe
    probe1 = ndx_extracellular_channels.Probe(
        name="probe1",
        identifier="7890",
        probe_model=probe_model1,
    )

    pi_probe1 = ndx_extracellular_channels.to_probeinterface(probe1)
    assert pi_probe1.ndim == 2
    assert pi_probe1.si_units == "um"
    assert pi_probe1.name == "probe1"
    assert pi_probe1.serial_number == "7890"
    assert pi_probe1.model_name == "Neuropixels 1.0"
    assert pi_probe1.manufacturer == "IMEC"
    npt.assert_array_equal(pi_probe1.contact_positions, probe_model1.contacts_table.relative_position_in_mm)
    npt.assert_array_equal(pi_probe1.contact_shapes, ["circle", "square"])
    npt.assert_array_equal(pi_probe1.to_numpy()["radius"], [10.0, np.nan])
    npt.assert_array_equal(pi_probe1.to_numpy()["width"], [np.nan, 10.0])
    npt.assert_array_equal(pi_probe1.to_numpy()["height"], [np.nan, 10.0])

    # add Probe as NWB Devices
    nwbfile.add_device(probe_model0)
    nwbfile.add_device(probe0)

    with pynwb.NWBHDF5IO("test_probeinterface.nwb", "w") as io:
        io.write(nwbfile)

    # read the file and test whether the read probe can be converted back to probeinterface correctly
    with pynwb.NWBHDF5IO("test_probeinterface.nwb", "r") as io:
        nwbfile = io.read()
        read_probe = nwbfile.devices["probe0"]
        pi_probe = ndx_extracellular_channels.to_probeinterface(read_probe)
        assert pi_probe.ndim == 2
        assert pi_probe.si_units == "um"
        assert pi_probe.name == "probe0"
        assert pi_probe.serial_number == "0123"
        assert pi_probe.model_name == "a1x32-edge-5mm-20-177_H32"
        assert pi_probe.manufacturer == "Neuronexus"
        npt.assert_array_equal(pi_probe.contact_positions, probe_model0.contacts_table.relative_position_in_mm)
        npt.assert_array_equal(pi_probe.to_numpy()["radius"], 5.0)
        npt.assert_array_equal(pi_probe.contact_shapes, "circle")
