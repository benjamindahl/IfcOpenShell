# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import json
import math
import ifcopenshell
import ifcopenshell.util.attribute
from mathutils import geometry
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


def draw_attributes(props, layout, copy_operator=None):
    for attribute in props:
        row = layout.row(align=True)
        draw_attribute(attribute, row, copy_operator)


def draw_attribute(attribute, layout, copy_operator=None):
    value_name = attribute.get_value_name()
    if not value_name:
        layout.label(text=attribute.name)
        return
    layout.prop(
        attribute,
        value_name,
        text=attribute.name,
    )
    if attribute.is_optional:
        layout.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")
    if copy_operator:
        op = layout.operator(f"{copy_operator}", text="", icon="COPYDOWN")
        op.name = attribute.name


def import_attributes(ifc_class, props, data, callback=None):
    for attribute in IfcStore.get_schema().declaration_by_name(ifc_class).all_attributes():
        import_attribute(attribute, props, data, callback=callback)


# A more elegant attribute importer signature, intended to supersede import_attributes
def import_attributes2(element, props, callback=None):
    for attribute in element.wrapped_data.declaration().as_entity().all_attributes():
        import_attribute(attribute, props, element.get_info(), callback=callback)


def import_attribute(attribute, props, data, callback=None):
    data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
    if isinstance(data_type, tuple) or data_type == "entity":
        callback(attribute.name(), None, data) if callback else None
        return
    new = props.add()
    new.name = attribute.name()
    new.is_null = data[attribute.name()] is None
    new.is_optional = attribute.optional()
    new.data_type = data_type if isinstance(data_type, str) else ""
    is_handled_by_callback = callback(attribute.name(), new, data) if callback else None
    if is_handled_by_callback:
        pass  # Our job is done
    elif is_handled_by_callback is False:
        props.remove(len(props) - 1)
    elif data_type == "string":
        new.string_value = "" if new.is_null else data[attribute.name()]
    elif data_type == "boolean":
        new.bool_value = False if new.is_null else data[attribute.name()]
    elif data_type == "integer":
        new.int_value = 0 if new.is_null else data[attribute.name()]
    elif data_type == "float":
        new.float_value = 0.0 if new.is_null else data[attribute.name()]
    elif data_type == "enum":
        new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
        if data[attribute.name()]:
            new.enum_value = data[attribute.name()]


def export_attributes(props, callback=None):
    attributes = {}
    for prop in props:
        is_handled_by_callback = callback(attributes, prop) if callback else False
        if is_handled_by_callback:
            continue  # Our job is done
        attributes[prop.name] = prop.get_value()
    return attributes


class IFCHeaderSpecs:
    def __init__(self, filepath: str):
        # According to https://www.steptools.com/stds/step/IS_final_p21e3.html#clause-8
        self.description = ""
        self.implementation_level = ""
        self.name = ""
        self.time_stamp = ""
        self.author = ""
        self.organization = ""
        self.preprocessor_version = ""
        self.originating_system = ""
        self.authorization = ""
        self.schema_name = ""
        with open(filepath) as ifc_file:
            max_lines_to_parse = 50
            for _ in range(max_lines_to_parse):
                line = next(ifc_file)
                if line.startswith("FILE_DESCRIPTION"):
                    for i, part in enumerate(line.split("'")):
                        if i == 1:
                            self.description = part
                        elif i == 3:
                            self.implementation_level = part
                elif line.startswith("FILE_NAME"):
                    for i, part in enumerate(line.split("'")):
                        if i == 1:
                            self.name = part
                        elif i == 3:
                            self.time_stamp = part
                elif line.startswith("FILE_SCHEMA"):                    
                    self.schema_name = line.split("'")[1]
                    break
