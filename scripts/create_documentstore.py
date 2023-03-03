import pandas as pd
import os
import dlite
import numpy as np
    

def from_csv_to_dlite_collection(path_to_csv: str, path_to_dlite_entity: str) -> dict:
    """ 
    Loads the csv file containing battery metadata (e.g. cathode, anode, cell type....)
    Loads the json file with the DLite entity.
    The properties of the metamodel must correspond with the columns in the csv file.
    Instantiates the DLite Entity and create instances from it, populated from the battery metadata csv file.
    Returns a collection of DLite instances, where each DLite instance corresponds to each row in the csv file.
    """
    
    battery_metadata_df     = pd.read_csv(path_to_csv, sep=',', header=0)
    battery_metadata_df.replace(np.nan, 0, inplace=True)

    battery_metadata_model  = dlite.Instance.from_url(f'json://{path_to_dlite_entity}')
    battery_repository_collection = dlite.Collection()

    # Create a DLite instance with data from for each row in the csv file
    for i in range(len(battery_metadata_df)):
        dlite_instance = battery_metadata_model() 

        for property in dlite_instance.properties:
            
            value = battery_metadata_df.loc[i][property] # Read the value of the property from the csv file
            setattr(dlite_instance, property, value)     # Set the corresponding dlite property

        battery_repository_collection.add(label=battery_metadata_df.loc[i]["cell_id"],
                                          inst=dlite_instance) 
    
    return battery_repository_collection




def save_document_store():
    """
    Creates DLite intances and populates them with data from BatteryArchive and Toyota Research Institute
    Saves the collection of instances as a json file.
    """
    # set directory information
    thisdir   = os.path.dirname(__file__)
    entitydir = '../entities'
    datadir   = '../data'

    repo_resources = {
            "Battery_Archive": {
                "entity": os.path.join(thisdir, entitydir, 'BatteryArchiveEntryMetadata.json'),
                "metadata": os.path.join(thisdir, datadir, 'battery_archive_data.csv')
                },
            "TRI_Dataset": {
                "entity": os.path.join(thisdir, entitydir, 'TRIEntryMetadata.json'),
                "metadata": os.path.join(thisdir, datadir, 'toyota_RI_metadata.csv')
                }
            }  
    dataset_collection = dlite.Collection()

    for key, resource in repo_resources.items():

        battery_repository_collection = from_csv_to_dlite_collection(resource["entity"], resource["metadata"])
        dataset_collection.add(label = key,
                               inst  = battery_repository_collection)

    
    dataset_collection.save('json', f'{thisdir}/{datadir}/Documentstore.json', 'mode=w')

    return dataset_collection



if __name__ == '__main__':
    dataset_collection = save_document_store()
    print("Collection saved")