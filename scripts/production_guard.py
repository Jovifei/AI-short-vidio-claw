#!/usr/bin/env python3
"""V5 entry point: use --plan, --approval, --registry, --workflow, --shot, --root.
Legacy approval manifests must be explicitly migrated; absence fails closed.
"""
import sys
from preproduction import main
if __name__ == '__main__':
    raise SystemExit(main(['guard', *sys.argv[1:]]))
