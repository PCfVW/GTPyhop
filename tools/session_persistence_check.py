#!/usr/bin/env python3
"""
Check that a saved PlannerSession can be read back by the release that saved it.

    python tools/session_persistence_check.py

Why this exists. Session persistence shipped in 1.3.0, stamping '1.3.0' into a
`version` field that validate_session_data gated on with startswith('1.'). The
2.0.0 packaging split bumped that stamp to '2.0.0' and left the gate alone, so
from 2.0.0 every file the library wrote was refused by the library that wrote
it: save_to_file returned True, the file on disk was perfectly well formed, and
load_from_file returned None. auto_save_sessions() wrote one such file per
session at exit, none of them loadable.

Nothing caught it because nothing exercised the round trip -- no test, no
doctest, no example referenced save_to_file or load_from_file anywhere outside
main.py. It was found by review, two releases later.

The first case below is the generic invariant that would have caught it without
anyone anticipating this particular mistake: whatever serialize_session stamps,
validate_session_data must accept. The rest pin the compatibility matrix, so a
future schema change cannot silently orphan existing files.
"""

import io
import json
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'packages', 'gtpyhop-core', 'src'))

_stdout = sys.stdout
sys.stdout = io.StringIO()
import gtpyhop                                                    # noqa: E402
from gtpyhop import Domain, PlannerSession                        # noqa: E402
from gtpyhop.main import (SessionSerializer, SESSION_SCHEMA_VERSION,   # noqa: E402
                          set_persistence_directory)
sys.stdout = _stdout

CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def quiet(fn, *args, **kwargs):
    """Call fn with stdout suppressed; the planner is chatty at import time."""
    out = sys.stdout
    sys.stdout = io.StringIO()
    try:
        return fn(*args, **kwargs)
    finally:
        sys.stdout = out


def a_session(name):
    return quiet(PlannerSession, domain=quiet(Domain, name), verbose=0)


def valid_payload(**extra):
    payload = {
        'session_id': 's',
        'verbose': 0,
        'recursive': False,
        'created_at': 0.0,
        'stats': {'plans_generated': 0, 'total_planning_time_ms': 0, 'errors': 0},
    }
    payload.update(extra)
    return payload


@case('what serialize stamps, validate accepts (the general invariant)')
def _():
    session = a_session('inv_roundtrip')
    raw = SessionSerializer.serialize_session(session)
    data = SessionSerializer.deserialize_session(raw)
    if not SessionSerializer.validate_session_data(data):
        return False, (f"serialize stamped schema_version="
                       f"{data.get('schema_version')!r} version="
                       f"{data.get('version')!r}, which validate rejects")
    return True, f"schema_version={data.get('schema_version')!r}"


@case('json round trip through the filesystem')
def _():
    path = os.path.join(tempfile.mkdtemp(), 'session.json')
    session = a_session('rt_json')
    if not quiet(session.save_to_file, path):
        return False, "save_to_file returned False"
    back = quiet(PlannerSession.load_from_file, path)
    if back is None:
        return False, "load_from_file returned None"
    if back.session_id != session.session_id:
        return False, f"session_id {back.session_id!r} != {session.session_id!r}"
    return True, "restored with matching session_id"


@case('pickle round trip through the filesystem')
def _():
    path = os.path.join(tempfile.mkdtemp(), 'session.pickle')
    session = a_session('rt_pickle')
    if not quiet(session.save_to_file, path, format='pickle'):
        return False, "save_to_file returned False"
    back = quiet(PlannerSession.load_from_file, path, format='pickle')
    return (back is not None), ("restored" if back else "load returned None")


@case('a file written by 1.3.0-1.9.7 still loads')
def _():
    path = os.path.join(tempfile.mkdtemp(), 'legacy.json')
    session = a_session('legacy_1x')
    quiet(session.save_to_file, path)
    data = json.load(open(path, encoding='utf-8'))
    data.pop('schema_version', None)          # the field did not exist then
    data['version'] = '1.3.0'
    json.dump(data, open(path, 'w', encoding='utf-8'))
    back = quiet(PlannerSession.load_from_file, path)
    return (back is not None), ("loaded" if back else "REFUSED a 1.x file")


@case('a file written by the broken 2.0.0/2.0.1 is rescued, not orphaned')
def _():
    path = os.path.join(tempfile.mkdtemp(), 'broken.json')
    session = a_session('legacy_20x')
    quiet(session.save_to_file, path)
    data = json.load(open(path, encoding='utf-8'))
    data.pop('schema_version', None)          # not written by those releases
    data['version'] = '2.0.0'
    json.dump(data, open(path, 'w', encoding='utf-8'))
    back = quiet(PlannerSession.load_from_file, path)
    return (back is not None), ("loaded" if back else "REFUSED a 2.0.x file")


@case('an unknown schema version is refused')
def _():
    accepted = SessionSerializer.validate_session_data(
        valid_payload(schema_version='99'))
    return (not accepted), ("refused" if not accepted
                            else "ACCEPTED an unknown schema")


@case('structural damage is still refused whatever the version says')
def _():
    good = valid_payload(schema_version=SESSION_SCHEMA_VERSION)
    checks = [
        ('empty stats', valid_payload(schema_version=SESSION_SCHEMA_VERSION,
                                      stats={})),
        ('missing session_id',
         {k: v for k, v in good.items() if k != 'session_id'}),
        ('wrong type for verbose',
         valid_payload(schema_version=SESSION_SCHEMA_VERSION, verbose='loud')),
    ]
    for label, payload in checks:
        if SessionSerializer.validate_session_data(payload):
            return False, f"accepted {label}"
    return True, f"{len(checks)} malformed payloads refused"


@case('an auto-saved file loads back')
def _():
    directory = tempfile.mkdtemp()
    quiet(set_persistence_directory, directory)
    session = a_session('autosave')
    path = os.path.join(directory, f"{session.session_id}.json")
    quiet(session.save_to_file, path)
    if not os.path.exists(path):
        return False, "auto-save path was not written"
    back = quiet(PlannerSession.load_from_file, path)
    return (back is not None), ("loaded" if back
                                else "auto-saved file is unloadable")


@case('a corrupt file is refused rather than half-loaded')
def _():
    path = os.path.join(tempfile.mkdtemp(), 'corrupt.json')
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write('{"session_id": "x"}')
    return (quiet(PlannerSession.load_from_file, path) is None), "refused"


def main():
    print("session persistence check\n")
    failed = 0
    for name, fn in CASES:
        try:
            ok, detail = fn()
        except Exception as exc:                                  # noqa: BLE001
            ok, detail = False, f"raised {exc!r}"
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            failed += 1
            print(f"        {detail}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
