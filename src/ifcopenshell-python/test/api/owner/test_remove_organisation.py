import test.bootstrap
import ifcopenshell.api


class TestRemoveOrganisation(test.bootstrap.IFC4):
    def test_removing_a_organisation(self):
        organisation = self.file.createIfcOrganization()
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcOrganization")) == 0

    def test_removing_roles_and_addresses_only_used_by_the_organisation(self):
        role = self.file.createIfcActorRole()
        address = self.file.createIfcPostalAddress()
        organisation = self.file.createIfcOrganization()
        organisation.Roles = [role]
        organisation.Addresses = [address]
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcOrganization")) == 0
        assert len(self.file.by_type("IfcActorRole")) == 0
        assert len(self.file.by_type("IfcPostalAddress")) == 0

    def test_not_removing_roles_and_addresses_used_elsewhere(self):
        role = self.file.createIfcActorRole()
        address = self.file.createIfcPostalAddress()
        organisation = self.file.createIfcOrganization()
        organisation2 = self.file.createIfcOrganization()
        organisation.Roles = [role]
        organisation.Addresses = [address]
        organisation2.Roles = [role]
        organisation2.Addresses = [address]
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcOrganization")) == 1
        assert len(self.file.by_type("IfcActorRole")) == 1
        assert len(self.file.by_type("IfcPostalAddress")) == 1

    def test_deleting_organisation_relationships_as_the_relating_organisation(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcOrganizationRelationship(RelatingOrganization=organisation)
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcOrganizationRelationship")) == 0

    def test_deleting_organisation_relationships_as_the_related_organisation(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcOrganizationRelationship(RelatedOrganizations=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcOrganizationRelationship")) == 0

    def test_deleting_person_and_organisations(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcPersonAndOrganization(TheOrganization=organisation)
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcPersonAndOrganization")) == 0

    def test_deleting_actors(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcActor(GlobalId=ifcopenshell.guid.new(), TheActor=organisation)
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcActor")) == 0

    def test_ensuring_document_information_should_not_be_left_in_an_invalid_set_cardinality(self):
        organisation = self.file.createIfcOrganization()
        document_information = self.file.createIfcDocumentInformation(Editors=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert document_information.Editors is None

    def test_deleting_resource_approval_relationships(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcResourceApprovalRelationship(RelatedResourceObjects=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcResourceApprovalRelationship")) == 0

    def test_deleting_resource_constraint_relationships(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcResourceConstraintRelationship(RelatedResourceObjects=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcResourceConstraintRelationship")) == 0

    def test_deleting_external_reference_relationships(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcExternalReferenceRelationship(RelatedResourceObjects=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcExternalReferenceRelationship")) == 0

    def test_deleting_an_application(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcApplication(ApplicationDeveloper=organisation)
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcApplication")) == 0
