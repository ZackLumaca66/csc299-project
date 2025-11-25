"""Run a robust CLI smoke test in a temporary directory.

This script runs several `pkms` CLI commands against a temp working
directory and ensures cleanup is safe on Windows by restoring the
original cwd before removing the temp directory.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pkms_core.cli import main


def run(args):
    print('\n$ pkms', ' '.join(args))
    try:
        main(args)
    except SystemExit as e:
        print(f'(exit {e.code})')


def smoke():
    orig_cwd = os.getcwd()
    td = tempfile.TemporaryDirectory()
    try:
        cwd = td.name
        print('Temp cwd for CLI test:', cwd)
        os.chdir(cwd)

        # Add tasks
        run(['add', 'Reply to Alice', '--backend', 'json'])
        run(['add', 'Pay invoice', '--priority', '4', '--backend', 'json'])
        run(['add', 'Plan sprint retro', '--priority', '3', '--backend', 'json'])

        # List (dashboard)
        run(['list', '--backend', 'json'])

        # Advise
        run(['advise', '--backend', 'json'])

        # Notes: add and list
        run(['notes', 'add', 'Capture quick idea about tests'])
        run(['notes', 'list'])

        # Export tasks+notes to file
        export_path = os.path.join(cwd, 'export.json')
        run(['export', export_path])
        try:
            print('Export file size:', os.path.getsize(export_path))
        except Exception:
            print('Export file not found')

        # Reset (wipe data)
        run(['reset', '--yes'])

        # Advise after reset (should be minimal)
        run(['advise', '--backend', 'json'])

    finally:
        # Restore original cwd before cleanup to avoid Windows permission errors
        try:
            os.chdir(orig_cwd)
        except Exception:
            pass
        try:
            td.cleanup()
        except Exception as e:
            print('Warning: failed to cleanup tempdir:', e)


if __name__ == '__main__':
    smoke()
