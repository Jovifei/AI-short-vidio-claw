#!/usr/bin/env python3
"""V5 queue: exact paths, file hashes, scoped approvals and motion-tier filtering."""
import sys
from preproduction import main
if __name__ == '__main__':
    raise SystemExit(main(['queue', *sys.argv[1:]]))
