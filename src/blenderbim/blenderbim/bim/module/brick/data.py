# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
from blenderbim.tool.brick import BrickStore

try:
    from rdflib import URIRef, BNode
except:
    # See #1860
    print("Warning: brickschema not available.")


def refresh():
    BrickschemaData.is_loaded = False
    BrickschemaReferencesData.is_loaded = False


class BrickschemaData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "is_loaded": cls.get_is_loaded(),
            "attributes": cls.attributes(),
            "namespaces": cls.namespaces(),
            "brick_equipment_classes": cls.brick_equipment_classes(),
        }

    @classmethod
    def get_is_loaded(cls):
        return BrickStore.graph is not None

    @classmethod
    def attributes(cls):
        if BrickStore.graph is None:
            return []
        props = bpy.context.scene.BIMBrickProperties
        try:
            brick = props.bricks[props.active_brick_index]
        except:
            return []
        results = []
        uri = brick.uri
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT ?name ?value ?sp ?sv WHERE {
               <{uri}> ?name ?value .
               OPTIONAL {
               { ?name rdfs:range brick:TimeseriesReference . }
                UNION
               { ?name a brick:EntityProperty . }
                ?value ?sp ?sv }
            }
        """.replace(
                "{uri}", uri
            )
        )

        for row in query:
            name = row.get("name").toPython().split("#")[-1]
            value = row.get("value")
            results.append(
                {
                    "name": name,
                    "value": value.toPython().split("#")[-1],
                    "is_uri": isinstance(value, URIRef),
                    "value_uri": value.toPython(),
                    "is_globalid": name == "globalID",
                }
            )
            if isinstance(row.get("value"), BNode):
                for s, p, o in BrickStore.graph.triples((value, None, None)):
                    results.append(
                        {
                            "name": name + ":" + p.toPython().split("#")[-1],
                            "value": o.toPython().split("#")[-1],
                            "is_uri": isinstance(o, URIRef),
                            "value_uri": o.toPython(),
                            "is_globalid": p.toPython().split("#")[-1] == "globalID",
                        }
                    )
        return results

    @classmethod
    def namespaces(cls):
        if BrickStore.graph is None:
            return []
        results = []
        for alias, uri in BrickStore.graph.namespaces():
            results.append((uri, f"{alias}: {uri}", ""))
        return results

    @classmethod
    def brick_equipment_classes(cls):
        if BrickStore.graph is None:
            return []
        results = []
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?class WHERE {
                ?class rdfs:subClassOf* brick:Equipment .
            }
        """
        )
        for uri in sorted([x[0].toPython() for x in query]):
            results.append((uri, uri.split("#")[-1], ""))
        return results


class BrickschemaReferencesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"is_loaded": cls.get_is_loaded(), "libraries": cls.libraries(), "references": cls.references()}

    @classmethod
    def get_is_loaded(cls):
        return BrickStore.graph is not None

    @classmethod
    def libraries(cls):
        results = []
        for library in tool.Ifc.get().by_type("IfcLibraryInformation"):
            if tool.Ifc.get_schema() == "IFC2X3":
                results.append((str(library.id()), library.Name or "Unnamed", ""))
            elif ".ttl" in library.Location:
                results.append((str(library.id()), library.Name or "Unnamed", ""))
        return results

    @classmethod
    def references(cls):
        results = []
        for rel in getattr(tool.Ifc.get_entity(bpy.context.active_object), "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesLibrary"):
                reference = rel.RelatingLibrary
                if tool.Ifc.get_schema() == "IFC2X3" and "#" not in reference.ItemReference:
                    continue
                if tool.Ifc.get_schema() != "IFC2X3" and "#" not in reference.Identification:
                    continue
                results.append(
                    {
                        "id": reference.id(),
                        "identification": reference.ItemReference
                        if tool.Ifc.get_schema() == "IFC2X3"
                        else reference.Identification,
                        "name": reference.Name or "Unnamed",
                    }
                )
        return results
