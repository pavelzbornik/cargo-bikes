"""Tests for schema validation."""


from scripts.bike_note_updater.schema_validator import SchemaValidator


class TestSchemaValidator:
    """Test SchemaValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator()

    def test_valid_minimal_frontmatter(self):
        """Test validation of minimal valid frontmatter."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike", "test"],
            "date": "2024-01-15",
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert report.is_valid

    def test_missing_required_field(self):
        """Test validation fails when required field is missing."""
        frontmatter = {
            "type": "bike",
            "tags": ["bike"],
            # Missing title and date
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any(issue.field == "title" for issue in report.issues)
        assert any(issue.field == "date" for issue in report.issues)

    def test_wrong_type_value(self):
        """Test validation fails when type is not 'bike'."""
        frontmatter = {
            "title": "Test",
            "type": "component",  # Wrong type
            "tags": ["bike"],
            "date": "2024-01-15",
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any(
            issue.field == "type" and issue.issue_type == "invalid_type"
            for issue in report.issues
        )

    def test_invalid_date_format(self):
        """Test validation fails for invalid date format."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike"],
            "date": "01/15/2024",  # Wrong format
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any(
            issue.field == "date" and issue.issue_type == "invalid_format"
            for issue in report.issues
        )

    def test_missing_bike_tag(self):
        """Test validation fails when 'bike' tag is missing."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["longtail", "trek"],  # Missing 'bike' tag
            "date": "2024-01-15",
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any(
            issue.field == "tags" and "bike" in issue.message.lower()
            for issue in report.issues
        )

    def test_tags_not_list(self):
        """Test validation fails when tags is not a list."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": "bike, longtail",  # Should be list
            "date": "2024-01-15",
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any(
            issue.field == "tags" and issue.issue_type == "invalid_type"
            for issue in report.issues
        )

    def test_tag_format_warning(self):
        """Test that improperly formatted tags generate warnings."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike", "LONGTAIL", "Cargo Bike"],  # Not normalized
            "date": "2024-01-15",
        }
        report = self.validator.validate_frontmatter(frontmatter)
        # Should have warnings about tag format
        assert len(report.warnings) > 0

    def test_legacy_fields_warning(self):
        """Test warning for legacy fields without specs."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
            "motor": "Bosch",  # Legacy field
            "battery": "500Wh",  # Legacy field
        }
        report = self.validator.validate_frontmatter(frontmatter)
        # Should warn about legacy fields
        assert any("legacy" in warning.lower() for warning in report.warnings)

    def test_valid_with_specs(self):
        """Test validation with specs structure."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike", "longtail"],
            "date": "2024-01-15",
            "specs": {
                "category": "longtail",
                "motor": {"make": "Bosch", "power_w": 250},
                "battery": {"capacity_wh": 500},
                "weight": {"with_battery_kg": 30},
            },
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert report.is_valid

    def test_specs_missing_recommended_fields(self):
        """Test that missing recommended spec fields don't fail validation."""
        frontmatter = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
            "specs": {
                "category": "longtail",
                # Missing motor, battery, weight - but these are recommended, not required
            },
        }
        report = self.validator.validate_frontmatter(frontmatter)
        # Should still be valid even without recommended fields
        assert report.is_valid

    def test_check_tag_format(self):
        """Test check_tag_format method."""
        valid_tags = ["bike", "longtail", "cargo-bike"]
        invalid_tags = ["bike", "LONGTAIL", "Cargo Bike"]

        assert self.validator.check_tag_format(valid_tags)
        assert not self.validator.check_tag_format(invalid_tags)

    def test_check_date_format(self):
        """Test check_date_format method."""
        assert self.validator.check_date_format("2024-01-15")
        assert not self.validator.check_date_format("01/15/2024")
        assert not self.validator.check_date_format("2024-13-01")


class TestValidateSpecsStructure:
    """Test specs structure validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator()

    def test_valid_motor_structure(self):
        """Test valid motor structure."""
        frontmatter = {
            "title": "Test",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
            "specs": {
                "motor": {"make": "Bosch", "model": "Performance Line"},
                "battery": {"capacity_wh": 500},
                "weight": {"with_battery_kg": 30},
                "category": "longtail",
            },
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert report.is_valid

    def test_motor_without_make_or_model(self):
        """Test that motor without make or model generates issue."""
        frontmatter = {
            "title": "Test",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
            "specs": {
                "motor": {"power_w": 250},  # No make or model
                "battery": {"capacity_wh": 500},
                "weight": {"with_battery_kg": 30},
                "category": "longtail",
            },
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any("motor" in issue.field.lower() for issue in report.issues)

    def test_battery_without_capacity(self):
        """Test that battery without capacity generates issue."""
        frontmatter = {
            "title": "Test",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
            "specs": {
                "motor": {"make": "Bosch"},
                "battery": {"removable": True},  # No capacity
                "weight": {"with_battery_kg": 30},
                "category": "longtail",
            },
        }
        report = self.validator.validate_frontmatter(frontmatter)
        assert not report.is_valid
        assert any("battery" in issue.field.lower() for issue in report.issues)

    def test_weight_without_values(self):
        """Test that weight without values generates issue."""
        frontmatter = {
            "title": "Test",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
            "specs": {
                "motor": {"make": "Bosch"},
                "battery": {"capacity_wh": 500},
                "weight": {},  # No weight values
                "category": "longtail",
            },
        }
        report = self.validator.validate_frontmatter(frontmatter)
        # Empty weight dict should generate an issue
        assert not report.is_valid
        assert any("weight" in issue.field.lower() for issue in report.issues)
