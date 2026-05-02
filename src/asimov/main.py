from __future__ import annotations

from pprint import pprint

from asimov.cycles.orchestrator import AsimovOrchestrator


def main() -> None:
    result = AsimovOrchestrator().run()
    pprint(result)


if __name__ == "__main__":
    main()
