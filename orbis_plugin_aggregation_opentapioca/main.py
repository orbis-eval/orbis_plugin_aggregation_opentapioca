# -*- coding: utf-8 -*-

import requests
import urllib.parse

from orbis_eval.core.base import AggregationBaseClass
from orbis_plugin_aggregation_opentapioca import types
from orbis_eval.plugins.orbis_plugin_aggregation_dbpedia_entity_types import Main as dbpedia_entity_types

import logging
logger = logging.getLogger(__name__)


class Main(AggregationBaseClass):

    def query(self, item):        
        data = item['corpus']
        service_url = self.get_service_url(data)
        logger.debug(f"OpenTapioca plugin query for: '{data}')")

        try:
            response = requests.get(service_url).json()
        except Exception as exception:
            logger.debug(f"Query failed: {exception}")
            response = None            
        return response

    def map_entities(self, response, item):
        file_entities = []

        if not response:
            return None
        
        if "annotations" in response:
            for annotation in response["annotations"]:
                if annotation["best_qid"] is not None and "tags" in annotation:
                    for tag in annotation["tags"]:
                        if tag["id"] == annotation["best_qid"]:
                            key = self.get_wikidata_url(tag["id"])
                            start = annotation["start"]
                            end = annotation["end"]
                            surfaceForm = self.get_surface_form(response["text"], start, end)
                            entity_type = self.get_type(tag["types"])
                            item = self.map_item(key, surfaceForm, entity_type, start, end)
                            if item is not None:
                                file_entities.append(item)

        return file_entities

    def map_tags(self, annotation, response):
        for tag in annotation["tags"]:
            if tag["id"] == annotation["best_qid"]:
                key = self.get_wikidata_url(tag["id"])
                start = annotation["start"]
                end = annotation["end"]
                surfaceForm = self.get_surface_form(response["text"], start, end)
                entity_type = self.get_type(tag["types"])
                return self.map_item(key, surfaceForm, entity_type, start, end)
        return None          

    def map_item(self, key, surfaceForm, entity_type, start, end):
        item = {
            "key": key,
            "surfaceForm": surfaceForm,
            "entity_type": entity_type,
            "document_start": start,
            "document_end": end
        }

        logger.debug(f"key: '{item['key']}', entity_type: '{item['entity_type']}', surfaceForm: '{item['surfaceForm']}', document_start: '{item['document_start']}', document_end: '{item['document_end']}'")
        return item

    def get_type(self, entity_types):
        entity_type = 'NoType'
        relevant_entities = [k for k in types.entities if types.entities[k] != entity_types[k] and entity_types[k] == True]
        if len(relevant_entities) == 1:
            entity_type = types.entities[relevant_entities[0]]
        else:
            relevant_properties = [k for k in types.properties if types.properties[k] != entity_types[k] and entity_types[k] == True]
            if len(relevant_properties) == 1:
                entity_type = types.properties[relevant_properties[0]]
        return dbpedia_entity_types.normalize_entity_type(entity_type)   

    def get_surface_form(self, text, start, end):
        return text[start:end]

    def get_wikidata_url(self, qId):
        return "https://www.wikidata.org/wiki/"+qId

    def get_service_url(self, query):
        args = {"query": query}
        service_url = "https://opentapioca.org/api/annotate?{}".format(urllib.parse.urlencode(args))
        return service_url
