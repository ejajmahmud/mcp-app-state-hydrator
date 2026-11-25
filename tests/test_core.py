"""Tests for MCP App State Hydrator."""
import unittest
from mcp_app_state_hydrator.core import MCPAppStateHydrator


class TestMCPAppStateHydrator(unittest.TestCase):
    def test_disjoint_merge_has_no_conflicts(self):
        h = MCPAppStateHydrator({"a": 1, "b": 2})
        res = h.reconcile({"a": 10}, {"b": 20})
        self.assertEqual(res["state"], {"a": 10, "b": 20})
        self.assertEqual(res["conflicts"], [])
        self.assertEqual(res["revision"], 1)

    def test_conflict_resolution_policies(self):
        h_srv = MCPAppStateHydrator({"mode": "auto"}, conflict_policy="server_wins")
        r1 = h_srv.reconcile({"mode": "manual"}, {"mode": "paused"})
        self.assertEqual(r1["state"]["mode"], "manual")
        self.assertEqual(len(r1["conflicts"]), 1)

        h_cli = MCPAppStateHydrator({"mode": "auto"}, conflict_policy="client_wins")
        r2 = h_cli.reconcile({"mode": "manual"}, {"mode": "paused"})
        self.assertEqual(r2["state"]["mode"], "paused")

    def test_identical_concurrent_edits_not_conflict(self):
        h = MCPAppStateHydrator({"x": 0})
        res = h.reconcile({"x": 5}, {"x": 5})
        self.assertEqual(res["conflicts"], [])

    def test_invalid_policy_raises(self):
        with self.assertRaises(ValueError):
            MCPAppStateHydrator({}, conflict_policy="random")
