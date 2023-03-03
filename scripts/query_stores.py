
from dlite.triplestore import Literal, Triplestore, SKOS
import warnings


HASPART          = 'http://emmo.info/emmo#EMMO_17e27c22_37e1_468c_9dd7_95e137f73e7f'
MAPSTO           = "http://emmo.info/domain-mappings#mapsTo"





def iri_to_preflabel(ts:Triplestore, iri:str)-> str:
    """
    Queries the triplestore for the IRI supplied, and retrievies its prefLabel if it exists.

    ts: Triplestore object.
    iri: IRI of the enetity.

    Eibar Flores, 2022, SINTEF Industry
    """

    # (IRI hasPrefLabel prefLable)
    prefLabel = list(ts.objects(subject=iri, predicate=SKOS.prefLabel))

    if len(prefLabel) == 1:
        return prefLabel[0].value

    else:
        warnings.warn(f"""The supplied IRI {iri} has {len(list(prefLabel))} prefLabels: {list(prefLabel)}""")
        return ""



def preflabel_to_iri(ts:Triplestore, prefLabel:str, lang:str=None) -> str:
    """
    Queries the triplestore for the prefLable supplied, and retrievies its IRI if it exists.

    ts: Triplestore object
    prefLabel: The prefLabel of the entity
    """

    # TODO: What if lang is no? or is it always en?
    if not lang:
        prefLabel_literal = Literal(prefLabel)
    else:
        prefLabel_literal = Literal(prefLabel, lang='en')

    # Make a list of all IRIs with the prefLabel
    iri = list(ts.subjects(predicate=SKOS.prefLabel, object=prefLabel_literal))

    if len(list(iri)) == 1:
        return iri[0]
    else:
        warnings.warn(f"""The supplied prefLabel {prefLabel} 
                         has {len(list(iri))} IRIs: {list(iri)}. Try adding the parameter lang=en""")
        return ""



def all_IRIs(ts:Triplestore) -> dict:
    """
    Returns a dictionary with all prefLable:IRI pairs in the triplestore.
    """

    iri_generator = ts.objects(predicate=MAPSTO)
    iris_dict = {}
    for iri in iri_generator:
        prefLabel = iri_to_preflabel(ts, iri)
        iris_dict[prefLabel]=iri

    return iris_dict



def find_uuids_from_IRI(ts: Triplestore, IRI:str)-> set[str]:
    """
    Returns the set of all uuid in the triplestore that has a property that maps to the IRI.
    """

    # Find properties that map to the IRI
    uuids_properties = ts.subjects(predicate = MAPSTO, object = IRI)

    # Find the uuids that are linked to these properties
    uuids = []
    for property in uuids_properties:
        uuid_generator = ts.subjects(predicate = HASPART, object = property)

        for uuid in uuid_generator:

            # Format uuids that have been appended with a default namespace
            if uuid.startswith("http"):
                uuid = uuid.split("/")[-1]    
            elif uuid.startswith("file"):
                uuid = uuid.split("/")[-1]
        uuids.append(uuid)

    return set(uuids)
