"""Unit and integration tests for the ndx_extracellular_channels types."""

from hdmf.common import DynamicTableRegion
import numpy as np
from pynwb import NWBFile
from pynwb.testing import TestCase, NWBH5IOFlexMixin

from ndx_extracellular_channels import (
    ProbeInsertion,
    ContactsTable,
    ProbeModel,
    Probe,
    ChannelsTable,
    ExtracellularSeries,
)


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
            contact_plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
            radius_in_um=10.0,
            width_in_um=np.nan,
            height_in_um=np.nan,
            device_channel_index_pi=1,  # TODO what is this for?
        )

        ct.add_row(
            relative_position_in_mm=[20.0, 10.0],
            shape="square",
            contact_id="C2",
            shank_id="shank0",
            contact_plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
            radius_in_um=np.nan,
            width_in_um=10.0,
            height_in_um=10.0,
            device_channel_index_pi=2,  # TODO what is this for?
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
        assert ct["contact_plane_axes"].data == [[[0.0, 1.0], [1.0, 0.0]], [[0.0, 1.0], [1.0, 0.0]]]
        assert ct["radius_in_um"].data == [10.0, np.nan]
        assert ct["width_in_um"].data == [np.nan, 10.0]
        assert ct["device_channel_index_pi"].data == [1, 2]


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
            contact_plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
            radius_in_um=10.0,
            width_in_um=np.nan,
            height_in_um=np.nan,
            device_channel_index_pi=1,  # TODO what is this for?
        )

        ct.add_row(
            relative_position_in_mm=[20.0, 10.0],
            shape="square",
            contact_id="C2",
            shank_id="shank0",
            contact_plane_axes=[[0.0, 1.0], [1.0, 0.0]],  # TODO make realistic
            radius_in_um=np.nan,
            width_in_um=10.0,
            height_in_um=10.0,
            device_channel_index_pi=2,  # TODO what is this for?
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
        ct = ContactsTable(  # NOTE: this must be named "contacts_table" when used in ProbeModel
            description="Test contacts table",
        )
        ct.add_row(
            relative_position_in_mm=[10.0, 10.0],
            shape="circle",
        )

        pm = ProbeModel(
            name="Neuropixels",
            description="A neuropixels probe",
            manufacturer="IMEC",
            model_name="Neuropixels 1.0",
            planar_contour=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],  # TODO make this optional
            contacts_table=ct,
        )

        assert pm.name == "Neuropixels"
        assert pm.description == "A neuropixels probe"
        assert pm.manufacturer == "IMEC"
        assert pm.model_name == "Neuropixels 1.0"
        assert pm.planar_contour == [[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]]
        assert pm.contacts_table is ct
        assert pm.ndim == 2


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
            name="Neuropixels",
            description="A neuropixels probe",
            manufacturer="IMEC",
            model_name="Neuropixels 1.0",
            planar_contour=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],  # TODO make this optional
            contacts_table=ct,
        )

        # TODO put this into /general/device_models
        self.nwbfile.add_device(pm)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.devices["Neuropixels"]


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
            name="Neuropixels",
            description="A neuropixels probe",
            manufacturer="IMEC",
            model_name="Neuropixels 1.0",
            planar_contour=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],  # TODO make this optional
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
            name="Neuropixels",
            description="A neuropixels probe",
            manufacturer="IMEC",
            model_name="Neuropixels 1.0",
            planar_contour=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],  # TODO make this optional
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
            name="Neuropixels",
            description="A neuropixels probe",
            manufacturer="IMEC",
            model_name="Neuropixels 1.0",
            planar_contour=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
            contacts_table=ct,
        )
        # TODO put this into /general/device_models
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
        name="Neuropixels",
        description="A neuropixels probe",
        manufacturer="IMEC",
        model_name="Neuropixels 1.0",
        planar_contour=[[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]],
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
        assert pi.reference is None
        assert pi.hemisphere is None
        assert pi.depth_in_mm is None
        # assert pi.insertion_position_in_mm is None
        # assert pi.insertion_angle_in_deg is None

    def test_constructor(self):
        pi = ProbeInsertion(
            name="ProbeInsertion",  # test custom name
            reference="Bregma at the cortical surface.",
            hemisphere="left",
            depth_in_mm=10.0,
            # insertion_position_in_mm=[2.0, -4.0, 0.0],  # TODO waiting on schema
            # insertion_angle_in_deg=[0.0, 0.0, -10.0],
        )

        assert pi.name == "ProbeInsertion"
        assert pi.reference == "Bregma at the cortical surface."
        assert pi.hemisphere == "left"
        assert pi.depth_in_mm == 10.0
        # assert pi.insertion_position_in_mm == [2.0, -4.0, 0.0]
        # assert pi.insertion_angle_in_deg == [0.0, 0.0, -10.0]


class TestProbeInsertionRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ProbeInsertion."""

    def getContainerType(self):
        return "ProbeInsertion"

    def addContainer(self):
        pi = ProbeInsertion(
            name="ProbeInsertion",  # test custom name
            reference="Bregma at the cortical surface.",
            hemisphere="left",
            depth_in_mm=10.0,
            # insertion_position_in_mm=[2.0, -4.0, 0.0],  # TODO waiting on schema
            # insertion_angle_in_deg=[0.0, 0.0, -10.0],
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
        ct.add_row()
        ct.add_row()

        assert len(ct) == 2
        assert ct.id.data == [0, 1]

    def test_constructor_add_row(self):
        """Test that the constructor for ChannelsTable sets values as expected."""
        probe = _create_test_probe()
        pi = ProbeInsertion()  # NOTE: this must be named "probe_insertion" when used in ChannelsTable

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",  # test custom name
            description="Test channels table",
            reference_mode="Reference to channel 2",
            probe=probe,
            probe_insertion=pi,
            target_tables={
                "contact": probe.probe_model.contacts_table,
                "reference_contact": probe.probe_model.contacts_table,
            },
            # TODO should not need to specify the above
        )

        ct.add_row(
            contact=0,
            reference_contact=2,
            filter="High-pass at 300 Hz",
            estimated_position_in_mm=[-1.5, 2.5, -2.5],
            estimated_brain_area="CA3",
            actual_position_in_mm=[-1.5, 2.4, -2.4],
            actual_brain_area="CA3",
        )

        ct.add_row(
            contact=1,
            reference_contact=2,
            filter="High-pass at 300 Hz",
            estimated_position_in_mm=[-1.5, 2.5, -2.4],
            estimated_brain_area="CA3",
            actual_position_in_mm=[-1.5, 2.4, -2.3],
            actual_brain_area="CA3",
        )

        # TODO might be nice to put this on the constructor of ContactsTable as relative_position__reference
        # without using a custom mapper
        ct["estimated_position_in_mm"].reference = "Bregma at the cortical surface"
        ct["actual_position_in_mm"].reference = "Bregma at the cortical surface"

        # TODO
        assert ct.name == "Neuropixels1ChannelsTable"
        # assert ...


class TestChannelsTableRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ChannelsTable."""

    def getContainerType(self):
        return "ChannelsTable"

    def addContainer(self):
        probe = _create_test_probe()
        self.nwbfile.add_device(probe.probe_model)  # TODO change to add_device_model
        self.nwbfile.add_device(probe)

        pi = ProbeInsertion(
            name="probe_insertion",
        )

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",  # test custom name
            description="Test channels table",
            reference_mode="Reference to channel 2",
            probe=probe,
            probe_insertion=pi,
            target_tables={
                "contact": probe.probe_model.contacts_table,
                "reference_contact": probe.probe_model.contacts_table,
            },
            # TODO should not need to specify the above
        )

        ct.add_row(
            contact=0,
            reference_contact=2,
            filter="High-pass at 300 Hz",
            estimated_position_in_mm=[-1.5, 2.5, -2.5],
            estimated_brain_area="CA3",
            actual_position_in_mm=[-1.5, 2.4, -2.4],
            actual_brain_area="CA3",
        )

        ct.add_row(
            contact=1,
            reference_contact=2,
            filter="High-pass at 300 Hz",
            estimated_position_in_mm=[-1.5, 2.5, -2.4],
            estimated_brain_area="CA3",
            actual_position_in_mm=[-1.5, 2.4, -2.3],
            actual_brain_area="CA3",
        )

        # TODO might be nice to put this on the constructor of ContactsTable as relative_position__reference
        # without using a custom mapper
        # TODO does matching this happen in the container equals roundtrip test?
        ct["estimated_position_in_mm"].reference = "Bregma at the cortical surface"
        ct["actual_position_in_mm"].reference = "Bregma at the cortical surface"

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
        ct.add_row()
        ct.add_row()
        ct.add_row()

        channels = DynamicTableRegion(
            name="channels",  # NOTE: this must be named "channels" when used in ExtracellularSeries
            data=[0, 1, 2],
            description="All of the channels",
            table=ct,
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

        # NOTE: the TimeSeries mapper maps spec "ExtracellularSeries/data/unit" to "ExtracellularSeries.unit"
        assert es.unit == "volts"
        assert es.timestamps_unit == "seconds"

        # TODO
        # assert ...


class TestExtracellularSeriesRoundTrip(NWBH5IOFlexMixin, TestCase):
    """Simple roundtrip test for a ExtracellularSeries."""

    def getContainerType(self):
        return "ExtracellularSeries"

    def addContainer(self):
        probe = _create_test_probe()
        self.nwbfile.add_device(probe.probe_model)  # TODO change to add_device_model
        self.nwbfile.add_device(probe)

        ct = ChannelsTable(
            name="Neuropixels1ChannelsTable",
            description="Test channels table",
            probe=probe,
        )
        ct.add_row()
        ct.add_row()
        ct.add_row()

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
            data=[[0.0, 1.0, 2.0], [1.0, 2.0, 3.0]],
            timestamps=[0.0, 0.001],
            channels=channels,
            channel_conversion=[1.0, 1.1, 1.2],
            conversion=1e5,
            offset=0.001,
            unit="volts",  # TODO should not have to specify this in init
        )
        self.nwbfile.add_acquisition(es)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.acquisition["ExtracellularSeries"]
