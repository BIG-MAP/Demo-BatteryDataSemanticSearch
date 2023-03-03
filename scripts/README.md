# Scripts
*Hannah Hansen, Cybernetics, NTNU*  
*Eibar Flores, Battery and Hydrogen Technologies, SINTEF INDUSTRY*  

These scripts use resources to build the demonstrator. Resources are files containing data (e.g. battery metadata csvs), mappings (column_name: IRI), DLite DataModels, and ontologies (e.g. battinfo.ttl).  

## Credit
* These scripts build on top of the code initially written by Hannah Hansen, currently stored in the directory scripts_hannah. 
* The code was further developed by Eibar Flores into the final version for the BIG-MAP workshop, Nov 29, 2022.


## Problems

* **Dlite cannot save NaNs**. When loading from a csv, if some row is NaN, DlIte can create an instance from it but when it saves to disk (e.g. json), it saves the nan not as Null, so Json gives error and it cannot be loaded. 
    * *Solution*: Replace NaN by 0 (float) when the proerty correspoding to the column is set to "float".
* **DLite cannot load the full collection**. A collection can be saved to disk as a json. But when the json needs to be opened, it requires to pass an uuid to create a single instance. Otherwise it throws an error. 
    * Code: `dlite_instance = dlite.Collection.from_location('json', path_to_collection)`
    * Error: `DLiteError: Error 1: id is required when loading from storage with more than one instance: path_to_collection/collection.json`
    * *Solution*: None, Collection is loaded as a python dict and manipulated in that way.
* **DLite cannot load the metadata from an instance saved in disk**.  
    * Code: `dlite_instance = dlite.Collection.from_url(f'json://{path_to_documentstore}#{key}')`
    * Error: `dlite_instance = dlite.Collection.from_url(f'json://{path_to_documentstore}#{key}')
  File "my_local_path\venv-dlite\lib\site-packages\dlite\dlite.py", line 1057, in from_url
    return Instance(
  File "my_local_path\venv-dlite\lib\site-packages\dlite\dlite.py", line 995, in __init__
    _dlite.Instance_swiginit(self, _dlite.new_Instance(*args, **kwargs))
dlite.DLiteError: Error 1: cannot find metadata 'http://onto-ns.com/meta/0.1/BatteryArchiveEntryMetadata' when loading 'd175c48d-6898-4eae-8923-2b45199afdaa' - please add the right storage to DLITE_STORAGES and try again
(venv-dlite)`
    * *Solution*: None, collection loaded as dictionary and handled in that way.
* **DLite cannot read csv from url**. Wuen trying to get a raw instance from an csv in an url, DLite throus error.
  * Code: `raw_data = dlite.Instance.from_location(driver='csv',location=url_to_csv)`. URL: "https://www.batteryarchive.org/data/CALCE_CX2-16_prism_LCO_25C_0-100_0.5-0.5C_a_timeseries.csv". Also tried to get the csv using a python request and decoding the payload, but shows same error.
  * Error: `DLiteError: cannot initiate dlite.Instance`
  * *Solution*: Use pandas, and create manually dlite instance from the pandas columns.
* **DLite crashes the Jupyter kernel used for prototyping** When creating an instance and passing the dimensions, the kernel crashes.
  * Code: `conformed_data = BatteryTimeSeriesData(dims=[10])`
  * Error in Jupyter notebook: `Canceled future for execute_request message before replies were done
The Kernel crashed while executing code in the the current cell or a previous cell. Please review the code in the cell(s) to identify a possible cause of the failure. Click here for more info. View Jupyter log for further details.`
  * *Solution*: Temporarily avoid DLite altogether, until its use and errors are better understood.


## Good to know
* **Leave Battinfo out of Triplestore?** If Battinfo is not parsed as part of the triplestore, you can still add triples. But you loose access to the prefLabel, definitions already in battinfo. Battinfo has around 14k triples, while the metadata triples accound for 7k triples. In terms of CPU time: leaving battinfo out takes 0.40625 s to load the triplestore. Keeping it in, takes  0.84375 s. Not much is saved.
* **Visualization is slow and not practical**. Initially we intended to access datasets from the web and show an interactive visualization. Datasets from the BA are accessible through their nice API, but are too heavy to be visualized in practical time. A dataset might contain 100k points so it takesd 10 s to donwload, 1 min to render the bokeh app, and 10 s for the bokeh app to respnd to user changes.
* **DLite enables search by str IRIs, RDFLIB not**. If the ontology is imported with rdflib, the searches .subjects(---) using the IRIs dont have any result. If using DLite instead, it works.