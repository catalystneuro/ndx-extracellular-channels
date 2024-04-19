# ndx-extracellular-channels



## Diagram


```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#ffffff', "primaryBorderColor': '#144E73', 'lineColor': '#D96F32'}}}%%


classDiagram
    direction LR

    class ExtracellularSeries {
        <<ElectricalSeries>>

        channels : DynamicTableRegion
        --> target : ChannelsTable
    }

    class ChannelsTable{
        <<DynamicTable>>
        --------------------------------------
        attributes
        --------------------------------------
        name : str
        description : str
        probe : ProbeModel
        probe_insertion : ProbeInsertion, optional
        contacts : DynamicTableRegion, optional?
        --> target : ContactsTable
        reference_contact :  DynamicTableRegion, optional
        --> target : ContactsTable
        reference_mode : Literal["external wire", ...], optional

        --------------------------------------
        columns
        --------------------------------------
        id : int
        filter : VectorData, optional
        ---> Values strings such as "Bandpass 0-300 Hz".
        contact_position [x, y, z] : VectorData, optional
        ---> Each value is length 3 tuple of floats.
        brain_area : VectorData, optional
        --> data : str
        ----> Plays the role of the old 'location'.
        ... Any other custom columns, such analong frontend e.g. ADC information
    }

    class ProbeInsertion {
        <<Container>>

        insertion_position : Tuple[float, float, float], optional
        ----> Stereotactic coordinates on surface.
        depth_in_um : float, optional
        insertion_angle : Tuple[float, float, float], optional
        ----> The pitch/roll/yaw relative to the position on the surface.
    }


    namespace ProbeInterface{
        class Probe {
                <<Device>>

                identifier : str
                --> Usually the serial number
                probe_model : ProbeModel
            }

            class ProbeModel {
                <<Not sure what type>>

                name : str
                manufactuer : str
                model : str
                contour : List[Tuple[float, float], Tuple[float, float, float]]
                contact_table : ContactsTable
            }

            class ContactTable {
                <<DynamicTable>>

                --------------------------------------
                attributes
                --------------------------------------
                name : str
                description : str
                
                --------------------------------------
                columns
                --------------------------------------
                id : int
                shape : str, optional
                size : str, optional
                shank_id : str, optional
                relative_position : List[Tuple[float, float], Tuple[float, float, float]], optional
            }
    }

 

    ExtracellularSeries ..> ChannelsTable : links with channels
    ProbeModel *--> ContactTable : contains
    Probe *..> ProbeModel : links with probe_model
    ChannelsTable *..> Probe : links  with probe

    ChannelsTable ..> ContactTable : links with contacts

    ChannelsTable *--> ProbeInsertion: might contain ProbeInsertion
    note for ChannelsTable "ChannelsTable is no longer global"
```