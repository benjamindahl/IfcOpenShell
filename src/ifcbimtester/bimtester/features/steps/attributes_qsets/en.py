from behave import step

# from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


# TODO: use get_psets from ifcopenshell.util.element
@step('All "{ifc_class}" elements have a "{qto_name}.{quantity_name}" quantity')
def step_impl(context, ifc_class, qto_name, quantity_name):
    elements = IfcStore.file.by_type(ifc_class)
    for element in elements:
        is_successful = False
        if not element.IsDefinedBy:
            assert False
        for relationship in element.IsDefinedBy:
            if relationship.RelatingPropertyDefinition.Name == qto_name:
                for quantity in relationship.RelatingPropertyDefinition.Quantities:
                    if quantity.Name == quantity_name:
                        is_successful = True
        if not is_successful:
            assert False
