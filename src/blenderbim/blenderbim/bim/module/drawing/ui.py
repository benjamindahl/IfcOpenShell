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
import blenderbim.bim.helper
import blenderbim.tool as tool
from bpy.types import Panel
from blenderbim.bim.module.drawing.data import TextData


class BIM_PT_camera(Panel):
    bl_label = "Drawing Generation"
    bl_idname = "BIM_PT_camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera and hasattr(context.active_object.data, "BIMCameraProperties")

    def draw(self, context):
        layout = self.layout

        if "/" not in context.active_object.name:
            layout.label(text="This is not a BIM camera.")
            return

        layout.use_property_split = True
        dprops = context.scene.DocProperties
        props = context.active_object.data.BIMCameraProperties

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(dprops, "has_underlay", icon="OUTLINER_OB_IMAGE")
        row.prop(dprops, "should_use_underlay_cache", text="", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(dprops, "has_linework", icon="IMAGE_DATA")
        row.prop(dprops, "should_use_linework_cache", text="", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(dprops, "has_annotation", icon="MOD_EDGESPLIT")
        row.prop(dprops, "should_use_annotation_cache", text="", icon="FILE_REFRESH")

        row = layout.row()
        row.prop(dprops, "should_extract")

        row = layout.row()
        row.prop(props, "is_nts")

        row = layout.row()
        row.operator("bim.generate_references")
        row = layout.row()
        row.operator("bim.resize_text")

        row = layout.row()
        row.prop(props, "target_view")

        row = layout.row()
        row.prop(props, "cut_objects")
        if props.cut_objects == "CUSTOM":
            row = layout.row()
            row.prop(props, "cut_objects_custom")

        row = layout.row()
        row.prop(props, "raster_x")
        row = layout.row()
        row.prop(props, "raster_y")

        row = layout.row()
        row.prop(props, "diagram_scale")
        if props.diagram_scale == "CUSTOM":
            row = layout.row()
            row.prop(props, "custom_diagram_scale")

        row = layout.row(align=True)
        row.operator("bim.create_drawing", text="Create Drawing", icon="OUTPUT")
        op = row.operator("bim.open_view", icon="URL", text="")
        op.view = context.active_object.name.split("/")[1]


class BIM_PT_drawing_underlay(Panel):
    bl_label = "Drawing Underlay"
    bl_idname = "BIM_PT_drawing_underlay"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BIM_PT_camera"

    @classmethod
    def poll(cls, context):
        return context.camera and hasattr(context.active_object.data, "BIMCameraProperties")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        dprops = context.scene.DocProperties
        props = context.active_object.data.BIMCameraProperties

        row = layout.row(align=True)
        row.operator("bim.add_drawing_style")

        if dprops.drawing_styles:
            layout.template_list("BIM_UL_generic", "", dprops, "drawing_styles", props, "active_drawing_style_index")

            if props.active_drawing_style_index < len(dprops.drawing_styles):
                drawing_style = dprops.drawing_styles[props.active_drawing_style_index]

                row = layout.row(align=True)
                row.prop(drawing_style, "name")
                row.operator("bim.remove_drawing_style", icon="X", text="").index = props.active_drawing_style_index

                row = layout.row()
                row.prop(drawing_style, "render_type")
                row = layout.row(align=True)
                row.prop(drawing_style, "vector_style")
                row.operator("bim.edit_vector_style", text="", icon="GREASEPENCIL")
                row = layout.row(align=True)
                row.prop(drawing_style, "include_query")
                row = layout.row(align=True)
                row.prop(drawing_style, "exclude_query")

                row = layout.row()
                row.operator("bim.add_drawing_style_attribute")

                for index, attribute in enumerate(drawing_style.attributes):
                    row = layout.row(align=True)
                    row.prop(attribute, "name", text="")
                    row.operator("bim.remove_drawing_style_attribute", icon="X", text="").index = index

                row = layout.row(align=True)
                row.operator("bim.save_drawing_style")
                row.operator("bim.activate_drawing_style")


class BIM_PT_drawings(Panel):
    bl_label = "SVG Drawings"
    bl_idname = "BIM_PT_drawings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.DocProperties

        row = layout.row(align=True)
        row.operator("bim.add_drawing")
        row.operator("bim.refresh_drawing_list", icon="FILE_REFRESH", text="")

        if props.drawings:
            if props.active_drawing_index < len(props.drawings):
                op = row.operator("bim.open_view", icon="URL", text="")
                op.view = props.active_drawing.name
                row.operator("bim.remove_drawing", icon="X", text="").index = props.active_drawing_index
            layout.template_list("BIM_UL_drawinglist", "", props, "drawings", props, "active_drawing_index")

        row = layout.row()
        row.operator("bim.add_ifc_file")

        for index, ifc_file in enumerate(props.ifc_files):
            row = layout.row(align=True)
            row.prop(ifc_file, "name", text="IFC #{}".format(index + 1))
            row.operator("bim.select_doc_ifc_file", icon="FILE_FOLDER", text="").index = index
            row.operator("bim.remove_ifc_file", icon="X", text="").index = index


class BIM_PT_schedules(Panel):
    bl_label = "ODS Schedules"
    bl_idname = "BIM_PT_schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        props = context.scene.DocProperties

        row = layout.row(align=True)
        row.operator("bim.add_schedule")

        if props.schedules:
            row.operator("bim.build_schedule", icon="LINENUMBERS_ON", text="")
            row.operator("bim.remove_schedule", icon="X", text="").index = props.active_schedule_index

            layout.template_list("BIM_UL_generic", "", props, "schedules", props, "active_schedule_index")

            row = layout.row()
            row.prop(props.active_schedule, "file")
            row.operator("bim.select_schedule_file", icon="FILE_FOLDER", text="")


class BIM_PT_sheets(Panel):
    bl_label = "SVG Sheets"
    bl_idname = "BIM_PT_sheets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        props = context.scene.DocProperties

        row = layout.row(align=True)
        row.prop(props, "titleblock", text="")
        row.operator("bim.add_sheet")

        if props.sheets:
            row.operator("bim.open_sheet", icon="URL", text="")
            row.operator("bim.remove_sheet", icon="X", text="").index = props.active_sheet_index

            layout.template_list("BIM_UL_generic", "", props, "sheets", props, "active_sheet_index")

        row = layout.row(align=True)
        row.operator("bim.add_drawing_to_sheet")
        row.operator("bim.add_schedule_to_sheet")
        row = layout.row()
        row.operator("bim.create_sheets")


class BIM_PT_text(Panel):
    bl_label = "IFC Text"
    bl_idname = "BIM_PT_text"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not context.active_object:
            return
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return
        return element.is_a("IfcAnnotation") and element.ObjectType in ["TEXT", "TEXT_LEADER"]

    def draw(self, context):
        if not TextData.is_loaded:
            TextData.load()

        self.layout.use_property_split = True
        props = context.active_object.BIMTextProperties

        if props.is_editing:
            row = self.layout.row(align=True)
            row.operator("bim.edit_text", icon="CHECKMARK")
            row.operator("bim.disable_editing_text", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(props.attributes, self.layout)
        else:
            row = self.layout.row()
            row.operator("bim.enable_editing_text", icon="GREASEPENCIL")

            for attribute in TextData.data["attributes"]:
                row = self.layout.row(align=True)
                row.label(text=attribute["name"])
                row.label(text=attribute["value"])

        row = self.layout.row()
        row.prop(props, "font_size")
        row = self.layout.row()
        row.prop(props, "symbol")
        row = self.layout.row()
        row.prop(props, "related_element")

        row = self.layout.row()
        row.operator("bim.add_variable")

        for index, variable in enumerate(props.variables):
            row = self.layout.row(align=True)
            row.prop(variable, "name")
            row.operator("bim.remove_variable", icon="X", text="").index = index
            row = self.layout.row()
            row.prop(variable, "prop_key")


class BIM_PT_annotation_utilities(Panel):
    bl_idname = "BIM_PT_annotation_utilities"
    bl_label = "Drawing"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("bim.clean_wireframes")
        row = layout.row(align=True)
        row.operator("bim.add_grid")
        row = layout.row(align=True)
        row.operator("bim.add_sections_annotations")

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Dim", icon="ARROW_LEFTRIGHT")
        op.object_type = "DIMENSION"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Dim (Eq)", icon="ARROW_LEFTRIGHT")
        op.object_type = "EQUAL_DIMENSION"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Text", icon="SMALL_CAPS")
        op.object_type = "TEXT"
        op.data_type = "empty"
        op = row.operator("bim.add_annotation", text="Leader", icon="TRACKING_BACKWARDS")
        op.object_type = "TEXT_LEADER"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Stair Arrow", icon="SCREEN_BACK")
        op.object_type = "STAIR_ARROW"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Hidden", icon="CON_TRACKTO")
        op.object_type = "HIDDEN_LINE"
        op.data_type = "mesh"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Level (Plan)", icon="SORTBYEXT")
        op.object_type = "PLAN_LEVEL"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Level (Section)", icon="TRIA_DOWN")
        op.object_type = "SECTION_LEVEL"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Breakline", icon="FCURVE")
        op.object_type = "BREAKLINE"
        op.data_type = "mesh"
        op = row.operator("bim.add_annotation", text="Misc", icon="MESH_MONKEY")
        op.object_type = "MISC"
        op.data_type = "mesh"

        props = context.scene.DocProperties

        row = layout.row(align=True)
        row.operator("bim.add_drawing")
        row.operator("bim.refresh_drawing_list", icon="FILE_REFRESH", text="")

        if props.drawings:
            if props.active_drawing_index < len(props.drawings):
                op = row.operator("bim.open_view", icon="URL", text="")
                op.view = props.active_drawing.name
                row.operator("bim.remove_drawing", icon="X", text="").index = props.active_drawing_index
            layout.template_list("BIM_UL_drawinglist", "", props, "drawings", props, "active_drawing_index")

        layout.prop(props, "should_draw_decorations")
        layout.prop(props, "decorations_colour")


class BIM_UL_drawinglist(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False)
            op = row.operator("bim.open_view_camera", icon="OUTLINER_OB_CAMERA", text="")
            op.view_name = item.name
        else:
            layout.label(text="", translate=False)
