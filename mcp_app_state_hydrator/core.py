"""Core 3-way state hydrator and conflict resolver for MCP App iframes."""
from typing import Any, Dict, List


class MCPAppStateHydrator:
    """Reconciles concurrent MCP server and client iframe state mutations."""

    def __init__(self, base_state: Dict[str, Any] = None, conflict_policy: str = "server_wins"):
        if conflict_policy not in ("server_wins", "client_wins"):
            raise ValueError("conflict_policy must be 'server_wins' or 'client_wins'")
        self.base_state = dict(base_state or {})
        self.conflict_policy = conflict_policy
        self.revision = 0

    def reconcile(
        self,
        server_patch: Dict[str, Any],
        client_patch: Dict[str, Any],
    ) -> Dict[str, Any]:
        merged = dict(self.base_state)
        conflicts: List[Dict[str, Any]] = []
        all_keys = set(server_patch.keys()) | set(client_patch.keys())

        for key in sorted(all_keys):
            in_srv = key in server_patch
            in_cli = key in client_patch
            if in_srv and not in_cli:
                merged[key] = server_patch[key]
            elif in_cli and not in_srv:
                merged[key] = client_patch[key]
            else:
                s_val = server_patch[key]
                c_val = client_patch[key]
                if s_val == c_val:
                    merged[key] = s_val
                else:
                    winner = s_val if self.conflict_policy == "server_wins" else c_val
                    merged[key] = winner
                    conflicts.append({
                        "key": key,
                        "server_value": s_val,
                        "client_value": c_val,
                        "resolved_to": self.conflict_policy,
                    })

        self.base_state = merged
        self.revision += 1
        return {
            "revision": self.revision,
            "state": dict(merged),
            "conflicts": conflicts,
        }
