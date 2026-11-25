"""CLI for MCP App State Hydrator."""
import argparse
import json
from .core import MCPAppStateHydrator


def main():
    parser = argparse.ArgumentParser(description="MCP App State Hydrator CLI")
    parser.add_argument("--policy", choices=["server_wins", "client_wins"], default="server_wins")
    args = parser.parse_args()

    hydrator = MCPAppStateHydrator({"page": 1, "query": "errors"}, conflict_policy=args.policy)
    out = hydrator.reconcile({"total": 42, "query": "warnings"}, {"page": 2, "query": "fatal"})
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
