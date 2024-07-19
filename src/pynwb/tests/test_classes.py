"""Unit and integration tests for the ndx_extracellular_channels types."""

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
from pynwb.testing import NWBH5IOFlexMixin, TestCase

from pynwb import NWBFile


class TestContactsTable(TestCase):
    """Simple unit test for creating a ContactsTable."""

    def test_constructor_minimal(self):
        ct = ContactsTable(
            description="Test contacts table",
        )
        assert ct.name == "contacts_table"
        assert len(ct) == 0

    def test_constructor_add_row(self):
        """Test that the constructor for ContactsTable sets values as expected."""
        ct = ContactsTable(
            name="ContactsTable",  # test custom name
            description="Test contacts table",
        )

        # for testing, mix and match different shapes. np.nan means the radius/width/height does not apply
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
            contact_id="C1",
            shank_id="shank0",
            plane_axes=[[1.0, 0.0], [0.0, 1.0]],
            radius_in_um=10.0,
            width_in_um=np.nan,
            height_in_um=np.nan,
            device_channel=1,
        )

        ct.add_row(
            relative_position_in_mm=[20.0, 10.0],
            shape="square",
            contact_id="C2",
            shank_id="shank0",
            plane_axes=[[1 / np.sqrt(2), 1 / np.sqrt(2)], [-1 / np.sqrt(2), 1 / np.sqrt(2)]],
            radius_in_um=np.nan,
            width_in_um=10.0,
            height_in_um=10.0,
            device_channel=2,
        )

        # TODO might be nice to put this on the constructor of ContactsTable as relative_position__reference
        # without using a custom mapper
        ct["relative_position_in_mm"].reference = "The bottom tip of the probe"

        assert ct.name == "ContactsTable"
        assert ct.description == "Test contacts table"
        assert ct["relative_position_in_mm"].reference == "The bottom tip of the probe"

        assert ct["relative_position_in_mm"].data == [[10.0, 10.0], [20.0, 10.0]]
        assert ct["shape"].data == ["circle", "square"]
        assert ct["contact_id"].data == ["C1", "C2"]
        assert ct["shank_id"].data == ["shank0", "shank0"]
        assert ct["plane_axes"].data == [
            [[1.0, 0.0], [0.0, 1.0]],
            [[1 / np.sqrt(2), 1 / np.sqrt(2)], [-1 / np.sqrt(2), 1 / np.sqrt(2)]],
        ]
        assert ct["radius_in_um"].data == [10.0, np.nan]
        assert ct["width_in_um"].data == [np.nan, 10.0]
        assert ct["device_channel"].data == [1, 2]


class TestContactsTableRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ContactsTable."""

    def getContainerType(self):
        return "ContactsTable"

    def addContainer(self):
        ct = ContactsTable(
            name="ContactsTable",  # test custom name
            description="Test contacts table",
        )

        # for testing, mix and match different shapes. np.nan means the radius/width/height does not apply
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
            contact_id="C1",
            shank_id="shank0",
            plane_axes=[[1.0, 0.0], [0.0, 1.0]],
            radius_in_um=10.0,
            width_in_um=np.nan,
            height_in_um=np.nan,
            device_channel=1,
        )

        ct.add_row(
            relative_position_in_mm=[20.0, 10.0],
            shape="square",
            contact_id="C2",
            shank_id="shank0",
            plane_axes=[[1 / np.sqrt(2), 1 / np.sqrt(2)], [-1 / np.sqrt(2), 1 / np.sqrt(2)]],
            radius_in_um=np.nan,
            width_in_um=10.0,
            height_in_um=10.0,
            device_channel=2,
        )

        # add the object into nwbfile.acquisition for testing
        # TODO after integration, put this into /general/extracellular_ephys
        self.nwbfile.add_acquisition(ct)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition["ContactsTable"]


class TestProbeModel(TestCase):
    """Simple unit test for creating a ProbeModel."""

    def test_constructor(self):
        """Test that the constructor for ProbeModel sets values as expected."""
        # NOTE: ContactsTable must be named "contacts_table" when used in ProbeModel. this is the default.
        ct = ContactsTable(
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            name="Neuropixels 1.0 Probe Model",
            model="Neuropixels 1.0",
            description="A neuropixels probe",
            manufacturer="IMEC",
            planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )

        assert pm.name == "Neuropixels 1.0 Probe Model"
        assert pm.model == "Neuropixels 1.0"
        assert pm.description == "A neuropixels probe"
        assert pm.manufacturer == "IMEC"
        assert pm.planar_contour_in_um == [[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]]
        assert pm.contacts_table is ct
        assert pm.ndim == 2

    def test_constructor_no_name(self):
        """Test that the constructor for ProbeModel sets values as expected."""
        ct = ContactsTable(
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            model="Neuropixels 1.0",
            description="A neuropixels probe",
            manufacturer="IMEC",
            planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )

        assert pm.name == "Neuropixels 1.0"


class TestProbeModelRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ProbeModel."""

    def getContainerType(self):
        return "ProbeModel"

    def addContainer(self):
        ct = ContactsTable(
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            name="Neuropixels 1.0 Probe Model",
            model="Neuropixels 1.0",
            description="A neuropixels probe",
            manufacturer="IMEC",
            planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )

        # TODO put this into /general/device_models
        self.nwbfile.add_device(pm)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.devices["Neuropixels 1.0 Probe Model"]


class TestProbe(TestCase):
    """Simple unit test for creating a Probe."""

    def test_constructor_minimal(self):
        """Test that the constructor for ProbeModel sets values as expected."""
        ct = ContactsTable(
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            description="A neuropixels probe",
            model="Neuropixels 1.0",
            manufacturer="IMEC",
            planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )

        probe = Probe(
            name="Neuropixels Probe 1",
            probe_model=pm,
        )

        assert probe.name == "Neuropixels Probe 1"
        assert probe.identifier is None
        assert probe.probe_model is pm

    def test_constructor(self):
        """Test that the constructor for ProbeModel sets values as expected."""
        ct = ContactsTable(
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            model="Neuropixels 1.0",
            description="A neuropixels probe",
            manufacturer="IMEC",
            planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )

        probe = Probe(
            name="Neuropixels Probe 1",
            identifier="28948291",
            probe_model=pm,
        )

        assert probe.identifier == "28948291"


class TestProbeRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a Probe."""

    def getContainerType(self):
        return "Probe"

    def addContainer(self):
        ct = ContactsTable(
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            model="Neuropixels 1.0",
            description="A neuropixels probe",
            manufacturer="IMEC",
            planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )
        # TODO after integration in core, change this to add_device_model which puts it in
        # /general/devices/models or /general/device_models.
        # Alternatively, ProbeModel is a child of Probe and if there are multiple Probe objects
        # that use the same ProbeModel, then create a link
        self.nwbfile.add_device(pm)

        probe = Probe(
            name="Neuropixels Probe 1",
            identifier="28948291",
            probe_model=pm,
        )
        self.nwbfile.add_device(probe)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.devices["Neuropixels Probe 1"]


def _create_test_probe():
    ct = ContactsTable(
        description="Test contacts table",
    )
    ct.add_row(
        relative_position_in_mm=[10.0, 10.0],
        shape="circle",
    )
    ct.add_row(
        relative_position_in_mm=[10.0, 10.0],
        shape="circle",
    )
    ct.add_row(
        relative_position_in_mm=[10.0, 10.0],
        shape="circle",
    )

    pm = ProbeModel(
        name="Neuropixels 1.0",
        model="Neuropixels 1.0",
        description="A neuropixels probe",
        manufacturer="IMEC",
        planar_contour_in_um=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
        contacts_table=ct,
    )

    probe = Probe(
        name="Neuropixels Probe 1",
        identifier="28948291",
        probe_model=pm,  # TODO rename as model?
    )
    return probe


class TestProbeInsertion(TestCase):
    """Simple unit test for creating a ProbeInsertion."""

    def test_constructor_minimal(self):
        pi = ProbeInsertion()
        assert pi.name == "probe_insertion"
        assert pi.position_reference is None
        assert pi.hemisphere is None
        assert pi.depth_in_mm is None
        assert pi.insertion_position_ap_in_mm is None
        assert pi.insertion_position_ml_in_mm is None
        assert pi.insertion_position_dv_in_mm is None
        assert pi.insertion_angle_roll_in_deg is None
        assert pi.insertion_angle_pitch_in_deg is None
        assert pi.insertion_angle_yaw_in_deg is None

    def test_constructor_with_depth(self):
        pi = ProbeInsertion(
            name="ProbeInsertion",  # test custom name
            position_reference="Bregma at the cortical surface.",
            hemisphere="left",
            depth_in_mm=10.0,
            insertion_position_ap_in_mm=2.0,
            insertion_position_ml_in_mm=-4.0,
            insertion_angle_roll_in_deg=-10.0,
            insertion_angle_pitch_in_deg=0.0,
            insertion_angle_yaw_in_deg=0.0,
        )

        assert pi.name == "ProbeInsertion"
        assert pi.position_reference == "Bregma at the cortical surface."
        assert pi.hemisphere == "left"
        assert pi.depth_in_mm == 10.0
        assert pi.insertion_position_ap_in_mm == 2.0
        assert pi.insertion_position_ml_in_mm == -4.0
        assert pi.insertion_position_dv_in_mm is None
        assert pi.insertion_angle_roll_in_deg == -10.0
        assert pi.insertion_angle_pitch_in_deg == 0.0
        assert pi.insertion_angle_yaw_in_deg == 0.0

    def test_constructor_with_dv(self):
        pi = ProbeInsertion(
            name="ProbeInsertion",  # test custom name
            position_reference="Bregma at the cortical surface.",
            hemisphere="left",
            insertion_position_ap_in_mm=2.0,
            insertion_position_ml_in_mm=-4.0,
            insertion_position_dv_in_mm=-10.0,
            insertion_angle_roll_in_deg=-10.0,
            insertion_angle_pitch_in_deg=0.0,
            insertion_angle_yaw_in_deg=0.0,
        )

        assert pi.name == "ProbeInsertion"
        assert pi.position_reference == "Bregma at the cortical surface."
        assert pi.hemisphere == "left"
        assert pi.insertion_position_ap_in_mm == 2.0
        assert pi.insertion_position_ml_in_mm == -4.0
        assert pi.insertion_position_dv_in_mm == -10.0
        assert pi.insertion_angle_roll_in_deg == -10.0
        assert pi.insertion_angle_pitch_in_deg == 0.0
        assert pi.insertion_angle_yaw_in_deg == 0.0


class TestProbeInsertionDepthRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ProbeInsertion."""

    def getContainerType(self):
        return "ProbeInsertion"

    def addContainer(self):
        pi = ProbeInsertion(
            name="ProbeInsertion",  # test custom name
            position_reference="Bregma at the cortical surface.",
            hemisphere="left",
            depth_in_mm=10.0,
            insertion_position_ap_in_mm=2.0,
            insertion_position_ml_in_mm=-4.0,
            insertion_angle_roll_in_deg=-10.0,
            insertion_angle_pitch_in_deg=0.0,
            insertion_angle_yaw_in_deg=0.0,
        )

        # put this in nwbfile.scratch for testing
        self.nwbfile.add_scratch(pi)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.scratch["ProbeInsertion"]


class TestProbeInsertionDVRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ProbeInsertion."""

    def getContainerType(self):
        return "ProbeInsertion"

    def addContainer(self):
        pi = ProbeInsertion(
            name="ProbeInsertion",  # test custom name
            position_reference="Bregma at the cortical surface.",
            hemisphere="left",
            depth_in_mm=10.0,
            insertion_position_ap_in_mm=2.0,
            insertion_position_ml_in_mm=-4.0,
            insertion_position_dv_in_mm=-10.0,
            insertion_angle_roll_in_deg=-10.0,
            insertion_angle_pitch_in_deg=0.0,
            insertion_angle_yaw_in_deg=0.0,
        )

        # put this in nwbfile.scratch for testing
        self.nwbfile.add_scratch(pi)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.scratch["ProbeInsertion"]


class TestChannelsTable(TestCase):
    """Simple unit test for creating a ChannelsTable."""

    def test_constructor_minimal(self):
        """Test that the constructor for ChannelsTable sets values as expected."""
        probe = _create_test_probe()

        ct = ChannelsTable(
            description="Test channels table",
            probe=probe,
        )

        assert ct.name == "ChannelsTable"
        assert ct.description == "Test channels table"
        assert ct.reference_mode is None
        assert ct.probe is probe
        assert len(ct) == 0

    def test_constructor_add_row_minimal(self):
        """Test that the constructor for ChannelsTable sets values as expected."""
        probe = _create_test_probe()

        ct = ChannelsTable(
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0)
        ct.add_row(contact=1)

        assert len(ct) == 2
        assert ct.id.data == [0, 1]
        assert ct["contact"].data == [0, 1]
        assert ct["contact"].table is probe.probe_model.contacts_table
        assert "reference_contact" not in ct.columns

    def test_constructor_add_row_with_reference(self):
        """Test that the constructor for ChannelsTable sets values as expected."""
        probe = _create_test_probe()

        ct = ChannelsTable(
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0, reference_contact=1)
        ct.add_row(contact=1, reference_contact=0)

        assert ct["reference_contact"].data == [1, 0]
        assert ct["reference_contact"].table is probe.probe_model.contacts_table

    def test_constructor_add_row(self):
        """Test that the constructor for ChannelsTable sets values as expected."""
        probe = _create_test_probe()
        # NOTE: ProbeInsertion must be named "probe_insertion" when used in ChannelsTable. this is the default.
        pi = ProbeInsertion()

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",  # test custom name
            description="Test channels table",
            reference_mode="Referenced to channel 2.",
            position_reference="(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface.",
            position_confirmation_method="Histology",
            probe=probe,
            probe_insertion=pi,
        )

        ct.add_row(
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

        ct.add_row(
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

        assert ct.name == "Neuropixels1ChannelsTable"
        assert ct.description == "Test channels table"
        assert ct.reference_mode == "Referenced to channel 2."
        assert ct.position_reference == "(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface."
        assert ct.position_confirmation_method == "Histology"
        assert ct.probe is probe
        assert ct.probe_insertion is pi
        assert len(ct) == 2
        assert ct["contact"].data == [0, 1]
        assert ct["contact"].table is probe.probe_model.contacts_table
        assert ct["reference_contact"].data == [2, 2]
        assert ct["reference_contact"].table is probe.probe_model.contacts_table
        assert ct["filter"].data == ["High-pass at 300 Hz", "High-pass at 300 Hz"]
        assert ct["estimated_position_ap_in_mm"].data == [2.0, 2.0]
        assert ct["estimated_position_ml_in_mm"].data == [-5.0, -4.9]
        assert ct["estimated_position_dv_in_mm"].data == [-9.5, -9.3]
        assert ct["estimated_brain_area"].data == ["CA3", "CA3"]
        assert ct["confirmed_position_ap_in_mm"].data == [2.0, 2.0]
        assert ct["confirmed_position_ml_in_mm"].data == [-4.9, -4.8]
        assert ct["confirmed_position_dv_in_mm"].data == [-9.5, -9.3]
        assert ct["confirmed_brain_area"].data == ["CA3", "CA3"]


class TestChannelsTableRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ChannelsTable."""

    def getContainerType(self):
        return "ChannelsTable"

    def addContainer(self):
        probe = _create_test_probe()
        self.nwbfile.add_device(probe.probe_model)  # TODO change to add_device_model after integration in core
        self.nwbfile.add_device(probe)

        pi = ProbeInsertion(
            name="probe_insertion",
        )

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",  # test custom name
            description="Test channels table",
            reference_mode="Referenced to channel 2.",
            position_reference="(AP, ML, DV) = (0, 0, 0) corresponds to bregma at the cortical surface.",
            position_confirmation_method="Histology",
            probe=probe,
            probe_insertion=pi,
        )

        ct.add_row(
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

        ct.add_row(
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
        self.nwbfile.add_acquisition(ct)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition["Neuropixels1ChannelsTable"]


class TestExtracellularSeries(TestCase):
    """Simple unit test for creating an ExtracellularSeries."""

    def test_constructor(self):
        probe = _create_test_probe()

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0)
        ct.add_row(contact=1)
        ct.add_row(contact=2)

        channels = DynamicTableRegion(
            name="channels",  # NOTE: this must be named "channels" when used in ExtracellularSeries
            data=[0, 1, 2],
            description="All of the channels",
            table=ct,
        )

        es = ExtracellularSeries(
            name="ExtracellularSeries",
            data=[[0.0, 1.0, 2.0], [1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]],
            timestamps=[0.0, 0.001, 0.002, 0.003],
            channels=channels,
            channel_conversion=[1.0, 1.1, 1.2],
            conversion=1e5,
            offset=0.001,
        )

        assert es.name == "ExtracellularSeries"
        assert es.data == [[0.0, 1.0, 2.0], [1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]]
        assert es.timestamps == [0.0, 0.001, 0.002, 0.003]
        assert es.channels is channels
        assert es.channel_conversion == [1.0, 1.1, 1.2]
        assert es.conversion == 1e5
        assert es.offset == 0.001
        # NOTE: the TimeSeries mapper maps spec "ExtracellularSeries/data/unit" to "ExtracellularSeries.unit"
        assert es.unit == "microvolts"
        assert es.timestamps_unit == "seconds"

    def test_constructor_channels_dim_transpose(self):
        probe = _create_test_probe()

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0)
        ct.add_row(contact=1)
        ct.add_row(contact=2)

        channels = DynamicTableRegion(
            name="channels",  # NOTE: this must be named "channels" when used in ExtracellularSeries
            data=[0, 1, 2],
            description="All of the channels",
            table=ct,
        )

        msg = (
            "ExtracellularSeries 'ExtracellularSeries': The length of the second dimension of `data` "
            "(4) does not match the length of `channels` (3), "
            "but instead the length of the first dimension does. `data` is oriented incorrectly and "
            "should be transposed."
        )
        with self.assertRaisesWith(ValueError, msg):
            ExtracellularSeries(
                name="ExtracellularSeries",
                data=[[0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0], [2.0, 3.0, 4.0, 5.0]],
                timestamps=[0.0, 0.001, 0.002, 0.003],
                channels=channels,
            )

    def test_constructor_channels_dim_mismatch(self):
        probe = _create_test_probe()

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0)
        ct.add_row(contact=1)
        ct.add_row(contact=2)

        channels = DynamicTableRegion(
            name="channels",  # NOTE: this must be named "channels" when used in ExtracellularSeries
            data=[0, 1, 2],
            description="All of the channels",
            table=ct,
        )

        msg = (
            "ExtracellularSeries 'ExtracellularSeries': The length of the second dimension of `data` "
            "(2) does not match the length of `channels` (3)."
        )
        with self.assertRaisesWith(ValueError, msg):
            ExtracellularSeries(
                name="ExtracellularSeries",
                data=[[0.0, 1.0], [1.0, 2.0], [2.0, 3.0], [3.0, 4.0]],
                timestamps=[0.0, 0.001, 0.002, 0.003],
                channels=channels,
            )

    def test_constructor_channel_conversion_dim_mismatch(self):
        probe = _create_test_probe()

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0)
        ct.add_row(contact=1)
        ct.add_row(contact=2)

        channels = DynamicTableRegion(
            name="channels",  # NOTE: this must be named "channels" when used in ExtracellularSeries
            data=[0, 1, 2],
            description="All of the channels",
            table=ct,
        )

        msg = (
            "ExtracellularSeries 'ExtracellularSeries': The length of the second dimension of `data` "
            "(3) does not match the length of `channel_conversion` (1)."
        )
        with self.assertRaisesWith(ValueError, msg):
            ExtracellularSeries(
                name="ExtracellularSeries",
                data=[[0.0, 1.0, 2.0], [1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]],
                timestamps=[0.0, 0.001, 0.002, 0.003],
                channels=channels,
                channel_conversion=[0.1],
            )


class TestExtracellularSeriesRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ExtracellularSeries."""

    def getContainerType(self):
        return "ExtracellularSeries"

    def addContainer(self):
        probe = _create_test_probe()
        self.nwbfile.add_device(probe.probe_model)  # TODO change to add_device_model after integration in core
        self.nwbfile.add_device(probe)

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",
            description="Test channels table",
            probe=probe,
        )
        ct.add_row(contact=0)
        ct.add_row(contact=1)
        ct.add_row(contact=2)

        # put this in nwbfile.acquisition for testing
        self.nwbfile.add_acquisition(ct)

        channels = DynamicTableRegion(
            name="channels",  # TODO I think this HAS to be named "channels"
            data=[0, 1, 2],
            description="All of the channels",
            table=ct,
        )

        es = ExtracellularSeries(
            name="ExtracellularSeries",
            data=[[0.0, 1.0, 2.0], [1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]],
            timestamps=[0.0, 0.001, 0.002, 0.003],
            channels=channels,
            channel_conversion=[1.0, 1.1, 1.2],
            conversion=1e5,
            offset=0.001,
        )
        self.nwbfile.add_acquisition(es)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition["ExtracellularSeries"]
