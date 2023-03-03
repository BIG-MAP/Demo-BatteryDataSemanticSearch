import os
import json
import dlite
from dlite.triplestore import Literal, Triplestore
#from tripper import Triplestore
import dlite.triplestore




# bind object and data properties
HASPART          = 'http://emmo.info/emmo#EMMO_17e27c22_37e1_468c_9dd7_95e137f73e7f'
MAPSTO           = "http://emmo.info/domain-mappings#mapsTo"


# ---------- ADDING TRIPLES TO TRIPLESTORE-------------


def get_key_from_value(dictionary:dict, value) -> str:
    """
    Returns the key in the dictionary with the given value.
    Retuns None if the given value is not found.
    """
    for key, val in dictionary.items():
        if val == value:
            return key
    return None


def add_concept_triples(ts:Triplestore, 
                        mapping:dict, 
                        dlite_instance_uuid:str, 
                        dlite_instance_properties:dict) -> None:
    """
    A function adding triples mapping the properties of a dlite instance to ontology concepts. 
    The properties are mapped to the IRIs in the mapping dictionary.

    ts: Triplestore in which to add the triples
    mappings: Dictionary with the property names as keys, and the corresponding IRI as the value. 
              The properties matche the columns in the metadata csv file.
    dlite_instance_uuid: The uuid of the dlite instance that is to be added into the triplestore
    dlite_instance_properties: A dictionary of the property:value pairs of the dlite instance
    """

    for property_name, iri in mapping.items():

        # If the property in the mapping file is also a property of the dlite instance,
        # a triple mapping this dlite instance property to the corresponding IRI is added.
        if property_name in dlite_instance_properties.keys():
            uuid_property = f'{dlite_instance_uuid}#{property_name}'
            ts.add((uuid_property,   MAPSTO, iri))

        # If the property in the mapping file is a value of the dlite instance,
        # a triple mapping the dlite instance property to the corresponding IRI is added.
        elif property_name in dlite_instance_properties.values():
            key = get_key_from_value(dictionary=dlite_instance_properties, value=property_name)
            uuid_property = f'{dlite_instance_uuid}#{key}'
            ts.add((uuid_property,   MAPSTO, iri))

            

def add_hasPart_triples(ts:Triplestore, dlite_instance_uuid:str, dlite_instance_properties:dict) -> None:
    """
    A function creating a link in the triplestore between the dlite intance and its properties
    using the hasPart data property.

    ts: Triplestore in which to add the triples
    dlite_instance_uuid: The uuid of the dlite instance
    dlite_instance_properties: A dictionary with properties:value pairs of the dlite instance
    """
        
    for property_name in dlite_instance_properties:
        uuid = dlite_instance_uuid
        uuid_property = f"{uuid}#{property_name}"
        ts.add((uuid, HASPART, uuid_property))   



def load_battery_data_triplestore() -> None:  
    """
    Creates a triplestore of the populated dlite instances in 
    documentstore.json, using the IRIs in the mapping files.
    The triplestore is saved as a n3 file.
    """

    # Set directory information
    thisdir               = os.path.dirname(__file__)
    path_to_battinfo      = os.path.join(thisdir, "../ontologies", 'battinfo-merged.ttl')
    path_to_documentstore = os.path.join(thisdir, '../data', 'Documentstore.json')
    path_to_ba_mappings   = os.path.join(thisdir, '../mappings', 'battery_archive_mappings.json')
    path_to_tri_mappings  = os.path.join(thisdir, '../mappings', 'toyota_RI_mappings.json')

    dest_path_to_ts = os.path.join(thisdir, "../ontologies", 'battery_data_triplestore.n3')
    
    # Load resources
    with open(path_to_documentstore) as f:
        documentstore_dict = json.load(f)

    with open(path_to_ba_mappings) as f:
        battery_archive_mappings = json.load(f)

    with open(path_to_tri_mappings) as f:
        tri_mappings = json.load(f)


    # Namespaces to identify in the collection
    battery_archive_meta = "http://onto-ns.com/meta/0.1/BatteryArchiveEntryMetadata"
    tri_instance_meta = "http://onto-ns.com/meta/0.1/TRIEntryMetadata"

    # Triplestore
    ts = Triplestore("rdflib") 
    ts.parse(path_to_battinfo)

    # Create triples from the populated dlite instances in documentstore_dict
    for key, value in documentstore_dict.items():

        # Determine which mapping file to use
        if value["meta"] == battery_archive_meta:
            mapping = battery_archive_mappings
        elif value["meta"] == tri_instance_meta:
            mapping = tri_mappings
        else:
            continue
    
        add_concept_triples(ts = ts, 
                            mapping = mapping, 
                            dlite_instance_properties = value["properties"],
                            dlite_instance_uuid = key)
        
        add_hasPart_triples(ts = ts, 
                            dlite_instance_properties = value["properties"],
                            dlite_instance_uuid = key)

    ts.serialize(destination = dest_path_to_ts)

    return ts
    



if __name__ == '__main__':

    ts = load_battery_data_triplestore()
    #Verify results
    print(f'Number of subjects: {len(list(ts.subjects()))}', '\n')