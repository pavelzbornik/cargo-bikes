"""Tests for the URL validator script."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scripts.validate_urls import (
    URLValidator,
    create_changelog_entry,
    extract_frontmatter,
    reconstruct_frontmatter,
    validate_and_clean_urls,
)


class TestURLValidator:
    """Tests for URLValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = URLValidator()

    def test_is_valid_url_with_valid_http_url(self):
        """Test valid HTTP URL."""
        assert self.validator.is_valid_url("http://example.com")

    def test_is_valid_url_with_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert self.validator.is_valid_url("https://example.com/path")

    def test_is_valid_url_with_invalid_url_no_scheme(self):
        """Test URL without scheme is invalid."""
        assert not self.validator.is_valid_url("example.com")

    def test_is_valid_url_with_invalid_url_no_netloc(self):
        """Test URL without netloc is invalid."""
        assert not self.validator.is_valid_url("http://")

    def test_is_valid_url_with_empty_string(self):
        """Test empty string is invalid."""
        assert not self.validator.is_valid_url("")

    def test_is_valid_url_with_none(self):
        """Test None is invalid."""
        assert not self.validator.is_valid_url(None)

    def test_is_valid_url_with_non_string(self):
        """Test non-string is invalid."""
        assert not self.validator.is_valid_url(123)


class TestExtractFrontmatter:
    """Tests for extract_frontmatter function."""

    def test_extract_valid_frontmatter(self):
        """Test extracting valid YAML frontmatter."""
        content = "---\ntitle: Test\ntype: bike\n---\nBody content"
        frontmatter, body, original_yaml = extract_frontmatter(content)
        assert frontmatter == {"title": "Test", "type": "bike"}
        assert body == "Body content"
        assert original_yaml is not None

    def test_extract_frontmatter_with_multiline_body(self):
        """Test extracting frontmatter with multiline body."""
        content = "---\ntitle: Test\n---\nLine 1\nLine 2"
        frontmatter, body, _original_yaml = extract_frontmatter(content)
        assert frontmatter == {"title": "Test"}
        assert body == "Line 1\nLine 2"

    def test_extract_no_frontmatter(self):
        """Test content without frontmatter."""
        content = "No frontmatter here"
        frontmatter, body, original_yaml = extract_frontmatter(content)
        assert frontmatter is None
        assert body == "No frontmatter here"
        assert original_yaml is None

    def test_extract_invalid_yaml(self):
        """Test invalid YAML frontmatter."""
        content = "---\ninvalid: [yaml:\n---\nBody"
        frontmatter, body, _original_yaml = extract_frontmatter(content)
        assert frontmatter is None
        assert body == content


class TestReconstructFrontmatter:
    """Tests for reconstruct_frontmatter function."""

    def test_reconstruct_simple_frontmatter(self):
        """Test reconstructing simple frontmatter."""
        frontmatter = {"title": "Test", "type": "bike"}
        body = "Body content"
        result = reconstruct_frontmatter(frontmatter, body)
        assert result.startswith("---\n")
        assert result.endswith("---\nBody content")
        assert "title: Test" in result

    def test_reconstruct_preserves_body(self):
        """Test that body content is preserved."""
        frontmatter = {"title": "Test"}
        body = "Line 1\nLine 2\nLine 3"
        result = reconstruct_frontmatter(frontmatter, body)
        assert result.endswith("Line 1\nLine 2\nLine 3")


class TestValidateAndCleanURLs:
    """Tests for validate_and_clean_urls function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = URLValidator()

    @patch.object(URLValidator, "check_url_reachable")
    def test_remove_invalid_url_field(self, mock_check):
        """Test setting invalid URL field to empty string."""
        mock_check.return_value = False
        frontmatter = {
            "title": "Test",
            "url": "https://invalid.example.com",
        }
        cleaned, removed = validate_and_clean_urls(frontmatter, self.validator)
        assert cleaned["url"] == ""
        assert removed == ["https://invalid.example.com"]

    @patch.object(URLValidator, "check_url_reachable")
    def test_remove_invalid_image_field(self, mock_check):
        """Test setting invalid image field to empty string."""
        mock_check.return_value = False
        frontmatter = {
            "title": "Test",
            "image": "https://invalid-image.example.com/pic.jpg",
        }
        cleaned, removed = validate_and_clean_urls(frontmatter, self.validator)
        assert cleaned["image"] == ""
        assert removed == ["https://invalid-image.example.com/pic.jpg"]

    @patch.object(URLValidator, "check_url_reachable")
    def test_keep_valid_urls(self, mock_check):
        """Test keeping valid URLs."""
        mock_check.return_value = True
        frontmatter = {
            "title": "Test",
            "url": "https://valid.example.com",
            "image": "https://valid-image.example.com/pic.jpg",
        }
        cleaned, removed = validate_and_clean_urls(frontmatter, self.validator)
        assert "url" in cleaned
        assert "image" in cleaned
        assert removed == []

    @patch.object(URLValidator, "check_url_reachable")
    def test_remove_multiple_invalid_urls(self, mock_check):
        """Test setting multiple invalid URLs to empty strings."""
        mock_check.return_value = False
        frontmatter = {
            "title": "Test",
            "url": "https://invalid1.example.com",
            "image": "https://invalid2.example.com/pic.jpg",
        }
        cleaned, removed = validate_and_clean_urls(frontmatter, self.validator)
        assert cleaned["url"] == ""
        assert cleaned["image"] == ""
        assert len(removed) == 2


class TestCreateChangelogEntry:
    """Tests for create_changelog_entry function."""

    def test_create_changelog_entry_with_removed_urls(self):
        """Test creating changelog entry with removed URLs."""
        entry = create_changelog_entry(
            "test/file.md",
            ["https://invalid.example.com"],
            "URLS_REMOVED",
        )
        assert entry["file"] == "test/file.md"
        assert entry["status"] == "URLS_REMOVED"
        assert entry["removed_urls"] == ["https://invalid.example.com"]
        assert "timestamp" in entry

    def test_create_changelog_entry_valid_urls(self):
        """Test creating changelog entry with valid URLs."""
        entry = create_changelog_entry("test/file.md", [], "OK_VALID_URLS")
        assert entry["file"] == "test/file.md"
        assert entry["status"] == "OK_VALID_URLS"
        assert entry["removed_urls"] == []


@pytest.mark.integration
class TestIntegration:
    """Integration tests."""

    def test_roundtrip_frontmatter(self):
        """Test extracting and reconstructing frontmatter."""
        original = "---\ntitle: Test Bike\ntype: bike\ntags: [bike]\n---\nBody"
        frontmatter, body, original_yaml = extract_frontmatter(original)
        reconstructed = reconstruct_frontmatter(frontmatter, body, original_yaml)

        # Extract again to verify round-trip
        frontmatter2, body2, _ = extract_frontmatter(reconstructed)
        assert frontmatter2 == frontmatter
        assert body2 == body


class TestURLValidatorCheckReachable:
    """Tests for URLValidator.check_url_reachable method."""

    @patch("requests.Session.head")
    def test_check_url_reachable_success(self, mock_head):
        """Test checking reachable URL."""
        mock_response = mock_head.return_value
        mock_response.status_code = 200

        validator = URLValidator()
        result = validator.check_url_reachable("https://example.com")
        assert result is True

    @patch("requests.Session.head")
    def test_check_url_reachable_redirect(self, mock_head):
        """Test checking URL with redirect."""
        mock_response = mock_head.return_value
        mock_response.status_code = 301

        validator = URLValidator()
        result = validator.check_url_reachable("https://example.com")
        assert result is True

    @patch("requests.Session.head")
    def test_check_url_reachable_not_found(self, mock_head):
        """Test checking URL that returns 404."""
        mock_response = mock_head.return_value
        mock_response.status_code = 404

        validator = URLValidator()
        result = validator.check_url_reachable("https://example.com")
        assert result is False

    @patch("requests.Session.head")
    def test_check_url_reachable_server_error(self, mock_head):
        """Test checking URL that returns 500."""
        mock_response = mock_head.return_value
        mock_response.status_code = 500

        validator = URLValidator()
        result = validator.check_url_reachable("https://example.com")
        assert result is False

    @patch("requests.Session.head")
    def test_check_url_reachable_connection_error(self, mock_head):
        """Test handling connection errors."""
        import requests

        mock_head.side_effect = requests.exceptions.ConnectionError("Connection failed")

        validator = URLValidator()
        result = validator.check_url_reachable("https://example.com")
        assert result is False

    def test_check_url_reachable_invalid_url(self):
        """Test checking invalid URL."""
        validator = URLValidator()
        result = validator.check_url_reachable("not-a-url")
        assert result is False

    @patch("requests.Session.head")
    def test_check_url_reachable_timeout_with_retry(self, mock_head):
        """Test handling timeout with retry logic."""
        import requests

        mock_head.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
        ]

        validator = URLValidator(max_retries=2)
        result = validator.check_url_reachable("https://example.com")
        assert result is False
        assert mock_head.call_count == 2

    @patch("requests.Session.head")
    def test_check_url_reachable_timeout_then_success(self, mock_head):
        """Test handling timeout that succeeds on retry."""
        import requests

        mock_response = mock_response = type("Response", (), {"status_code": 200})()
        mock_head.side_effect = [
            requests.exceptions.Timeout(),
            mock_response,
        ]

        validator = URLValidator(max_retries=2)
        result = validator.check_url_reachable("https://example.com")
        assert result is True
