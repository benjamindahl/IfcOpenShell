#include "../../../ifcparse/IfcParse.h"

#include "CgalKernel.h"
#include "CgalConversionResult.h"

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcRepresentation* l, ConversionResults& shapes) {
	IfcSchema::IfcRepresentationItem::list::ptr items = l->Items();
	bool part_succes = false;
	if (items->size()) {
		for (IfcSchema::IfcRepresentationItem::list::it it = items->begin(); it != items->end(); ++it) {
			IfcSchema::IfcRepresentationItem* representation_item = *it;
			if (shape_type(representation_item) == ST_SHAPELIST) {
				part_succes |= convert_shapes(*it, shapes);
			} else {
				cgal_shape_t s;
				if (convert_shape(representation_item, s)) {
					shapes.push_back(ConversionResult(new CgalShape(s), get_style(representation_item)));
					part_succes |= true;
				}
			}
		}
	}
	return part_succes;
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcExtrudedAreaSolid*, cgal_shape_t&) {
	throw std::runtime_error("Not implemented IfcExtrudedAreaSolid");
}

bool IfcGeom::CgalKernel::convert(const IfcSchema::IfcCartesianPoint* l, cgal_point_t& point) {
//  IN_CACHE(IfcCartesianPoint,l,gp_Pnt,point)
//  std::vector<double> xyz = l->Coordinates();
//  point = gp_Pnt(
//                 xyz.size()     ? (xyz[0]*getValue(GV_LENGTH_UNIT)) : 0.0f,
//                 xyz.size() > 1 ? (xyz[1]*getValue(GV_LENGTH_UNIT)) : 0.0f,
//                 xyz.size() > 2 ? (xyz[2]*getValue(GV_LENGTH_UNIT)) : 0.0f
//                 );
//  CACHE(IfcCartesianPoint,l,point)
  return true;
}
