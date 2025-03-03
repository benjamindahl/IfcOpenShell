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

import os
import bpy
import brickschema
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from rdflib.namespace import RDF
from rdflib import Literal, URIRef, Namespace
from test.bim.bootstrap import NewFile
from blenderbim.tool.brick import Brick as subject
from blenderbim.tool.brick import BrickStore


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Brick)


class TestAddBrick(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.Graph()
        result = subject.add_brick(
            "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment"
        )
        assert "http://example.org/digitaltwin#" in result
        assert list(
            BrickStore.graph.triples((URIRef(result), RDF.type, URIRef("https://brickschema.org/schema/Brick#Equipment")))
        )
        assert list(
            BrickStore.graph.triples(
                (URIRef(result), URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Unnamed"))
            )
        )


class TestAddBrickBreadcrumb(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        subject.add_brick_breadcrumb()
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[0].name == "brick_class"
        subject.add_brick_breadcrumb()
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[1].name == "brick_class"


class TestAddBrickFromElement(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcChiller()
        element.Name = "Chiller"
        element.GlobalId = ifcopenshell.guid.new()
        BrickStore.graph = brickschema.Graph()
        result = subject.add_brick_from_element(
            element, "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment"
        )
        uri = f"http://example.org/digitaltwin#{element.GlobalId}"
        assert result == uri
        assert list(
            BrickStore.graph.triples((URIRef(uri), RDF.type, URIRef("https://brickschema.org/schema/Brick#Equipment")))
        )
        assert list(
            BrickStore.graph.triples(
                (URIRef(uri), URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Chiller"))
            )
        )


class TestAddBrickifcProject(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        project = ifc.createIfcProject(ifcopenshell.guid.new())
        project.Name = "My Project"
        BrickStore.graph = brickschema.Graph()
        result = subject.add_brickifc_project("http://example.org/digitaltwin#")
        assert result == f"http://example.org/digitaltwin#{project.GlobalId}"
        brick = URIRef(result)
        assert list(
            BrickStore.graph.triples((brick, RDF.type, URIRef("https://brickschema.org/extension/ifc#Project")))
        )
        assert list(
            BrickStore.graph.triples(
                (brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("My Project"))
            )
        )
        assert list(
            BrickStore.graph.triples(
                (brick, URIRef("https://brickschema.org/extension/ifc#projectID"), Literal(project.GlobalId))
            )
        )
        assert list(
            BrickStore.graph.triples(
                (
                    brick,
                    URIRef("https://brickschema.org/extension/ifc#fileLocation"),
                    Literal(bpy.context.scene.BIMProperties.ifc_file),
                )
            )
        )


class TestAddBrickifcReference(NewFile):
    def test_run(self):
        TestAddBrickifcProject().test_run()
        element = tool.Ifc.get().createIfcChiller(ifcopenshell.guid.new())
        project = URIRef(f"http://example.org/digitaltwin#{tool.Ifc.get().by_type('IfcProject')[0].GlobalId}")
        subject.add_brickifc_reference("http://example.org/digitaltwin#foo", element, project)
        brick = URIRef("http://example.org/digitaltwin#foo")
        bnode = list(
            BrickStore.graph.triples((brick, URIRef("https://brickschema.org/extension/ifc#hasIFCReference"), None))
        )[0][2]
        assert list(
            BrickStore.graph.triples(
                (bnode, URIRef("https://brickschema.org/extension/ifc#hasProjectReference"), project)
            )
        )
        assert list(
            BrickStore.graph.triples(
                (bnode, URIRef("https://brickschema.org/extension/ifc#globalID"), Literal(element.GlobalId))
            )
        )


class TestAddFeed(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.Graph()
        subject.add_feed("http://example.org/digitaltwin#source", "http://example.org/digitaltwin#destination")
        assert list(
            BrickStore.graph.triples(
                (
                    URIRef("http://example.org/digitaltwin#source"),
                    URIRef("https://brickschema.org/schema/Brick#feeds"),
                    URIRef("http://example.org/digitaltwin#destination"),
                )
            )
        )


class TestClearBrickBrowser(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.bricks.add()
        subject.clear_brick_browser()
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 0


class TestClearProject(NewFile):
    def test_run(self):
        BrickStore.graph = "graph"
        bpy.context.scene.BIMBrickProperties.active_brick_class == "brick_class"
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "foo"
        subject.clear_project()
        assert BrickStore.graph is None
        assert bpy.context.scene.BIMBrickProperties.active_brick_class == ""
        assert len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) == 0


class TestExportBrickAttributes(NewFile):
    def test_run(self):
        assert subject.export_brick_attributes("http://example.org/digitaltwin#floor") == {
            "Identification": "http://example.org/digitaltwin#floor",
            "Name": "floor",
        }

    def test_run_ifc2x3(self):
        tool.Ifc.set(ifcopenshell.file(schema="IFC2X3"))
        assert subject.export_brick_attributes("http://example.org/digitaltwin#floor") == {
            "ItemReference": "http://example.org/digitaltwin#floor",
            "Name": "floor",
        }


class TestGetActiveBrickClass(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        assert subject.get_active_brick_class() == "brick_class"


class TestGetBrick(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcChiller()
        library = ifc.createIfcLibraryReference(Identification="http://example.org/digitaltwin#globalid")
        ifc.createIfcRelAssociatesLibrary(RelatedObjects=[element], RelatingLibrary=library)
        assert subject.get_brick(element) == "http://example.org/digitaltwin#globalid"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        element = ifc.createIfcEnergyConversionDevice()
        library = ifc.createIfcLibraryReference(ItemReference="http://example.org/digitaltwin#globalid")
        ifc.createIfcRelAssociatesLibrary(RelatedObjects=[element], RelatingLibrary=library)
        assert subject.get_brick(element) == "http://example.org/digitaltwin#globalid"


class TestGetBrickClass(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcAirTerminalBox()
        assert subject.get_brick_class(element) == "https://brickschema.org/schema/Brick#TerminalUnit"


class TestGetBrickPath(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        cwd = os.path.dirname(os.path.realpath(__file__))
        assert subject.get_brick_path() == os.path.join(cwd, "..", "files", "spaces.ttl")


class TestGetBrickPathName(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        assert subject.get_brick_path_name() == "spaces.ttl"


class TestGetBrickifcProject(NewFile):
    def test_run(self):
        TestAddBrickifcProject().test_run()
        assert (
            subject.get_brickifc_project()
            == f"http://example.org/digitaltwin#{tool.Ifc.get().by_type('IfcProject')[0].GlobalId}"
        )


class TestGetConvertableBrickObjectsAndElements(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAirTerminalBox()
        obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, obj)
        ifc.createIfcWall()
        assert subject.get_convertable_brick_objects_and_elements() == [(obj, element)]


class TestGetItemClass(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        assert subject.get_item_class("http://example.org/digitaltwin#floor") == "Floor"


class TestGetLibraryBrickReference(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        library = ifc.createIfcLibraryInformation()
        reference = ifc.createIfcLibraryReference(
            Identification="http://example.org/digitaltwin#floor", ReferencedLibrary=library
        )
        assert subject.get_library_brick_reference(library, "http://example.org/digitaltwin#floor") == reference

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        reference = ifc.createIfcLibraryReference(ItemReference="http://example.org/digitaltwin#floor")
        library = ifc.createIfcLibraryInformation(LibraryReference=[reference])
        assert subject.get_library_brick_reference(library, "http://example.org/digitaltwin#floor") == reference


class TestGetNamespace(NewFile):
    def test_run(self):
        assert subject.get_namespace("http://example.org/digitaltwin#globalid") == "http://example.org/digitaltwin#"


class TestImportBrickClasses(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_classes("Class")
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 2
        brick = bpy.context.scene.BIMBrickProperties.bricks[0]
        assert brick.name == "Building"
        assert brick.uri == "https://brickschema.org/schema/Brick#Building"
        assert brick.total_items == 1
        assert not brick.label
        brick = bpy.context.scene.BIMBrickProperties.bricks[1]
        assert brick.name == "Location"
        assert brick.uri == "https://brickschema.org/schema/Brick#Location"
        assert brick.total_items == 1
        assert not brick.label


class TestImportBrickItems(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_items("Building")
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 1
        brick = bpy.context.scene.BIMBrickProperties.bricks[0]
        assert brick.name == "bldg"
        assert brick.label == "My Building"
        assert brick.uri == "http://example.org/digitaltwin#bldg"
        assert brick.total_items == 0


class TestLoadBrickFile(NewFile):
    def test_run(self):
        # We stub the schema to make tests run faster
        BrickStore.schema = brickschema.Graph()
        cwd = os.path.dirname(os.path.realpath(__file__))
        schema_path = os.path.join(cwd, "..", "files", "BrickStub.ttl")
        BrickStore.schema.load_file(schema_path)

        # This is the actual test
        cwd = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(cwd, "..", "files", "spaces.ttl")
        subject.load_brick_file(filepath)
        assert BrickStore.graph


class TestNewBrickFile(NewFile):
    def test_run(self):
        # We stub the schema to make tests run faster
        BrickStore.schema = brickschema.Graph()
        cwd = os.path.dirname(os.path.realpath(__file__))
        schema_path = os.path.join(cwd, "..", "files", "BrickStub.ttl")
        BrickStore.schema.load_file(schema_path)

        # This is the actual test
        subject.new_brick_file()
        assert BrickStore.graph
        namespaces = [(ns[0], ns[1].toPython()) for ns in BrickStore.graph.namespaces()]
        assert ("digitaltwin", "https://example.org/digitaltwin#") in namespaces
        assert ("brick", "https://brickschema.org/schema/Brick#") in namespaces
        assert ("rdfs", "http://www.w3.org/2000/01/rdf-schema#") in namespaces


class TestPopBrickBreadcrumb(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "bar"
        assert subject.pop_brick_breadcrumb() == "bar"
        assert len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) == 1
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[0].name == "foo"


class TestRunAssignBrickReference(NewFile):
    def test_nothing(self):
        pass


class TestRunRefreshBrickViewer(NewFile):
    def test_nothing(self):
        pass


class TestViewBrickClass(NewFile):
    def test_nothing(self):
        pass


class TestSelectBrowserItem(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        assert bpy.context.scene.BIMBrickProperties.active_brick_class == "brick_class"


class TestSetActiveBrickClass(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.bricks.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.bricks.add().name = "bar"
        subject.select_browser_item("namespace#bar")
        assert bpy.context.scene.BIMBrickProperties.active_brick_index == 1
