import streamlit as st
import os
import json
import sys
from dlite.triplestore import  Triplestore

THISDIR = os.path.realpath(os.path.dirname(__file__))
SCRIPTDIR = os.path.join(THISDIR, f'../scripts/')
ONTODIR = os.path.join(THISDIR, f'../ontologies/')
sys.path.insert(1, SCRIPTDIR)

import query_stores as qs




######################################## INITIALIZATION FUNCTIONS ############################################# 


#@st.cache() #Namespace object cannot be cached
def load_triplestore()-> Triplestore:
    #can be replaced with a connection to a remote triplestore, enabling search by triples.
    
    ts = Triplestore("rdflib") 
    ts.parse(os.path.join(THISDIR, ONTODIR, "battery_data_triplestore.n3"))
    
    return ts


#@st.cache()
def load_documentstore()-> dict:

    #can be replaced with a connection to a remote database, enabling search by uuids.
    with open(os.path.join(os.path.realpath(os.path.dirname(__file__)),
                         f'../data/Documentstore.json')) as f:
        
        documentstore = json.load(f)
    
    return documentstore




############################################# GLOBAL VARIABLES #################################################



TRIPLESTORE   = load_triplestore()
DOCUMENTSTORE = load_documentstore()
SEARCH_SCHEMA = qs.all_IRIs(TRIPLESTORE)
URLS = {"timeseries_url":"Time series",
        "cycleseries_url": "Cycle series",
        "repository_url": "Repository"}


st.session_state["search"] = {}
st.session_state["results"] = {}




############################################# CALLBACKS ################################################# 



def callback_search_button(search_pattern):   


    if len(search_pattern)>0:

        uuids_for_each_iri = [qs.find_uuids_from_IRI(ts=TRIPLESTORE, IRI=iri)  for iri in search_pattern.values()]
        
        uuids_common_to_all_searched_iris = set.intersection(*uuids_for_each_iri)

        uuid_dict = {uuid:DOCUMENTSTORE[uuid]["properties"] for uuid in uuids_common_to_all_searched_iris}

        if uuid_dict: 
            st.session_state["results"] = uuid_dict





############################################# APP ################################################# 


# --- HEADER ----

st.markdown("# Battery Data Semantic Search")
st.markdown("""Search for open repositories with battery data. 
                We use the Battery Interface Ontology [BattINFO](https://github.com/BIG-MAP/BattINFO) 
                to index multiple data repositories, and leverage semantic search to find datasets.
                When possible, the datasets can be downloaded, visualized and explored interactively.""")





# ------ SIDEBAR ----

st.sidebar.markdown("## Prepare your search")



st.sidebar.markdown("""Select ontology concepts to search by. """)

with st.sidebar.form(key="search_form"):

    search_concepts: list = st.multiselect("Search by", SEARCH_SCHEMA.keys(), label_visibility= "collapsed")


    search_pattern = {key:value for key, value in SEARCH_SCHEMA.items() if key in search_concepts}


    search_button = st.form_submit_button("Search")



if search_button:
    #st.sidebar.markdown("debugging")
    #st.sidebar.json(search_pattern)
    callback_search_button(search_pattern)



# ---- RESULTS ----

st.markdown("### Browse results") 


if search_button:

    search_hits = st.session_state["results"]

    # # Show user table CODE FROM Constantine_Kurbatov, https://discuss.streamlit.io/t/make-streamlit-table-results-hyperlinks-or-add-radio-buttons-to-table/7883/2
    colms = st.columns((1, 4))
    fields = ["Item №", 'Cell ID']
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)

    for x, (uuid, uuid_field) in enumerate(search_hits.items()):

        col1, col2= st.columns((1, 4))

        col1.write(x)  # index

        with col2.expander(uuid_field["cell_id"]):  # cell_id

            for url_key, url_name in URLS.items():

                if url_key in uuid_field.keys():

                    st.markdown('[{}]({})'.format(url_name, uuid_field[url_key]), 
                                unsafe_allow_html=True)
                    
                    uuid_field.pop(url_key)

            st.markdown("Metadata")
            st.json(uuid_field)





