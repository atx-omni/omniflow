import json
import tempfile
import unittest
from pathlib import Path

from omniflow.diff.diff_engine import diff_graphs
from omniflow.diff.semantic_graph import build_graph
from omniflow.reporting.junit_report import to_junit
from omniflow.reporting.sarif_report import to_sarif
from omniflow.validators.yaml_lint import has_error, lint_graph
from omniflow.yaml_pull import pull_yaml


class FakeYamlClient:
    def get_model_yaml(self, *args, **kwargs):
        return {
            "files": {"views/orders.view": "name: orders\nfields:\n  id:\n    primary_key: true\n"},
            "checksums": {"views/orders.view": "abc"},
        }


class DiffLintReportTests(unittest.TestCase):
    def test_yaml_pull_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = pull_yaml(
                client=FakeYamlClient(),
                model_id="model-1",
                branch_id="branch-1",
                output_dir=tmp,
            )
            self.assertTrue((Path(tmp) / "views/orders.view").exists())
            self.assertEqual(manifest["files"]["views/orders.view"]["checksum"], "abc")

    def test_semantic_diff_detects_deleted_field_and_type_change(self):
        base = build_graph({"views/orders.view": {"name": "orders", "fields": {"id": {"type": "number"}, "revenue": {"type": "number"}}}})
        head = build_graph({"views/orders.view": {"name": "orders", "fields": {"id": {"type": "string"}}}})
        report = diff_graphs(base, head)
        types = {change["type"] for change in report["changes"]}
        self.assertIn("field_deleted", types)
        self.assertIn("field_type_changed", types)
        self.assertEqual(report["risk_level"], "breaking")

    def test_rule_severity_handling(self):
        graph = build_graph({"views/orders.view": {"name": "orders", "fields": {"revenue": {"type": "number"}}}})
        issues = lint_graph(graph, configured_rules={"require_primary_keys": "error"})
        self.assertTrue(has_error(issues))

    def test_sarif_and_junit_output(self):
        report = {"tool_version": "0.4.0", "issues": [{"rule_id": "x", "severity": "error", "file": "a.yml", "message": "bad"}]}
        sarif = to_sarif(report)
        junit = to_junit(report)
        self.assertEqual(sarif["version"], "2.1.0")
        self.assertIn("<failure", junit)


if __name__ == "__main__":
    unittest.main()

