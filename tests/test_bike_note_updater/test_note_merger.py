"""Tests for note merging logic."""


from scripts.bike_note_updater.note_merger import NoteMerger


class TestNoteMerger:
    """Test NoteMerger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.merger = NoteMerger(conflict_threshold=0.1)

    def test_merge_empty_new_data(self):
        """Test merging with empty new data."""
        existing = {
            "title": "Test Bike",
            "type": "bike",
            "tags": ["bike"],
            "date": "2024-01-15",
        }
        new_data = {}

        result = self.merger.merge(existing, new_data)
        assert result.merged_frontmatter == existing
        assert len(result.conflicts) == 0

    def test_merge_update_image(self):
        """Test updating image URL."""
        existing = {
            "title": "Test Bike",
            "image": "old-image.jpg",
        }
        new_data = {
            "image": "new-image.jpg",
        }

        result = self.merger.merge(existing, new_data)
        assert result.merged_frontmatter["image"] == "new-image.jpg"
        assert "image" in result.changes_made

    def test_merge_update_url(self):
        """Test updating product URL."""
        existing = {
            "title": "Test Bike",
            "url": "https://old-url.com",
        }
        new_data = {
            "url": "https://new-url.com",
        }

        result = self.merger.merge(existing, new_data)
        assert result.merged_frontmatter["url"] == "https://new-url.com"
        assert "url" in result.changes_made

    def test_merge_title_change_creates_conflict(self):
        """Test that title changes create a conflict."""
        existing = {
            "title": "Old Title",
        }
        new_data = {
            "title": "New Title",
        }

        result = self.merger.merge(existing, new_data)
        assert result.merged_frontmatter["title"] == "New Title"
        assert len(result.conflicts) > 0
        assert result.conflicts[0].field == "title"

    def test_merge_resellers(self):
        """Test updating resellers."""
        existing = {
            "title": "Test Bike",
            "resellers": [{"name": "Old Store", "price": 5000}],
        }
        new_data = {
            "resellers": [{"name": "New Store", "price": 4500}],
        }

        result = self.merger.merge(existing, new_data)
        assert len(result.merged_frontmatter["resellers"]) == 1
        assert result.merged_frontmatter["resellers"][0]["name"] == "New Store"
        assert "resellers" in result.changes_made

    def test_merge_specs_simple(self):
        """Test merging simple specs."""
        existing = {
            "specs": {
                "category": "longtail",
                "model_year": 2023,
            }
        }
        new_data = {
            "specs": {
                "category": "longtail",
                "model_year": 2024,
            }
        }

        result = self.merger.merge(existing, new_data)
        assert result.merged_frontmatter["specs"]["model_year"] == 2024
        assert "specs" in result.changes_made

    def test_merge_nested_motor_specs(self):
        """Test merging nested motor specs."""
        existing = {
            "specs": {
                "motor": {
                    "make": "Bosch",
                    "power_w": 250,
                }
            }
        }
        new_data = {
            "specs": {
                "motor": {
                    "make": "Bosch",
                    "power_w": 250,
                    "torque_nm": 85,  # Added field
                }
            }
        }

        result = self.merger.merge(existing, new_data)
        assert result.merged_frontmatter["specs"]["motor"]["torque_nm"] == 85
        assert result.merged_frontmatter["specs"]["motor"]["make"] == "Bosch"

    def test_merge_significant_numeric_change_creates_conflict(self):
        """Test that significant numeric changes create conflicts."""
        existing = {
            "specs": {
                "motor": {
                    "power_w": 250,
                }
            }
        }
        new_data = {
            "specs": {
                "motor": {
                    "power_w": 350,  # 40% increase - significant
                }
            }
        }

        result = self.merger.merge(existing, new_data)
        assert len(result.conflicts) > 0
        # Should still update the value
        assert result.merged_frontmatter["specs"]["motor"]["power_w"] == 350

    def test_merge_minor_numeric_change_no_conflict(self):
        """Test that minor numeric changes don't create conflicts."""
        existing = {
            "specs": {
                "motor": {
                    "power_w": 250,
                }
            }
        }
        new_data = {
            "specs": {
                "motor": {
                    "power_w": 255,  # 2% increase - minor
                }
            }
        }

        result = self.merger.merge(existing, new_data)
        # Minor change shouldn't create conflict
        assert len(result.conflicts) == 0
        assert result.merged_frontmatter["specs"]["motor"]["power_w"] == 255

    def test_merge_motor_model_change_creates_conflict(self):
        """Test that motor model changes create major conflicts."""
        existing = {
            "specs": {
                "motor": {
                    "model": "Performance Line",
                }
            }
        }
        new_data = {
            "specs": {
                "motor": {
                    "model": "Cargo Line",
                }
            }
        }

        result = self.merger.merge(existing, new_data)
        assert len(result.conflicts) > 0
        assert result.conflicts[0].conflict_type == "major"

    def test_preserved_sections(self):
        """Test that preserved sections are recorded."""
        existing = {"title": "Test"}
        new_data = {"title": "Test Updated"}
        preserve_sections = ["references", "user-reviews"]

        result = self.merger.merge(existing, new_data, preserve_sections)
        assert "references" in result.preserved_sections
        assert "user-reviews" in result.preserved_sections


class TestDetectConflicts:
    """Test conflict detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.merger = NoteMerger(conflict_threshold=0.1)

    def test_detect_no_conflict_same_value(self):
        """Test no conflict when values are the same."""
        conflict = self.merger.detect_conflicts(100, 100)
        assert conflict is None

    def test_detect_no_conflict_none_old_value(self):
        """Test no conflict when old value is None."""
        conflict = self.merger.detect_conflicts(None, 100)
        assert conflict is None

    def test_detect_conflict_significant_numeric(self):
        """Test conflict detection for significant numeric changes."""
        conflict = self.merger.detect_conflicts(100, 150)
        assert conflict is not None
        assert conflict.conflict_type == "major"

    def test_detect_no_conflict_minor_numeric(self):
        """Test no conflict for minor numeric changes."""
        conflict = self.merger.detect_conflicts(100, 105)
        assert conflict is None

    def test_detect_conflict_motor_model_change(self):
        """Test conflict for motor model changes."""
        conflict = self.merger._detect_value_conflict(
            "specs.motor.model", "Performance Line", "Cargo Line"
        )
        assert conflict is not None
        assert conflict.conflict_type == "major"


class TestMergeNestedSpec:
    """Test merging nested specifications."""

    def setup_method(self):
        """Set up test fixtures."""
        self.merger = NoteMerger()

    def test_merge_nested_adds_new_fields(self):
        """Test that merging adds new fields."""
        old_dict = {
            "make": "Bosch",
            "power_w": 250,
        }
        new_dict = {
            "make": "Bosch",
            "power_w": 250,
            "torque_nm": 85,
        }

        merged, _conflicts = self.merger._merge_nested_spec("motor", old_dict, new_dict)
        assert merged["torque_nm"] == 85
        assert merged["make"] == "Bosch"

    def test_merge_nested_updates_existing_fields(self):
        """Test that merging updates existing fields."""
        old_dict = {
            "capacity_wh": 500,
            "removable": True,
        }
        new_dict = {
            "capacity_wh": 625,
            "removable": True,
        }

        merged, _conflicts = self.merger._merge_nested_spec(
            "battery", old_dict, new_dict
        )
        assert merged["capacity_wh"] == 625
        assert merged["removable"] is True

    def test_merge_deeply_nested(self):
        """Test merging deeply nested structures."""
        old_dict = {
            "dimensions": {
                "length_cm": 200,
            }
        }
        new_dict = {
            "dimensions": {
                "length_cm": 200,
                "width_cm": 80,
            }
        }

        merged, _conflicts = self.merger._merge_nested_spec("frame", old_dict, new_dict)
        assert merged["dimensions"]["length_cm"] == 200
        assert merged["dimensions"]["width_cm"] == 80
