#!/usr/bin/env python3
import argparse
import os
import sys
import xml.etree.ElementTree as ET

__version__ = "0.1"


TEST_IMPL_DIR = 'qa/'


def get_all_files_from_dir(path, extension, condition):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.{}'.format(extension)) and condition(os.path.join(r, file)):
                files.append(os.path.join(r, file))
    return files


def check_if_test_spec_file(path):
    return ET.parse(path).getroot().tag == 'test'


def check_if_test_impl_file(path):
    with open(path, 'r') as f:
        return "*** Test Cases ***" in f.read()


def ts_get_ti_path(path):
    node = ET.parse(path).getroot().find('robotframeworkfile')
    if node is not None:
        ti_path = node.text
        return ti_path
    else:
        return ''


def check_ts2ti_mapping(ts_files, ti_files):
    for ts in ts_files:
        ts_robot_path = ts_get_ti_path(ts)
        if ts_robot_path and TEST_IMPL_DIR in ts_robot_path:
            ts_robot_path = ts_robot_path.split(TEST_IMPL_DIR)[1]
            if not [ti for ti in ti_files if ts_robot_path in ti]:
                print("No TI: {} for TS: {}!!!".format(ts_robot_path, ts))
        else:
            print("Invalid robot file path in {}: {}".format(ts, str(ts_robot_path)))


def check_ti2ts_mapping(ti_files, ts_files):
    for ti in ti_files:
        found = False
        ti_path = ti.split(TEST_IMPL_DIR)[1]
        for ts in ts_files:
            ts_robot_path = ts_get_ti_path(ts)
            if ts_robot_path and TEST_IMPL_DIR in ts_robot_path:
                ts_robot_path = ts_robot_path.split(TEST_IMPL_DIR)[1]
            if ti_path == ts_robot_path:
                found = True
                break
        if not found:
            print("No TS for TI: {}".format(ti_path))


def main():
    parser = argparse.ArgumentParser(description=
                                     'Check mapping between Test Specification (xml) and Implementation (robot)')
    parser.add_argument('ts_dir', help='path to the Test Specification root directory (XML files)')
    parser.add_argument('ti_dir', help='path to the Test Implementation root directory (robot files)')
    parser.add_argument('-r', dest='revert', action='store_true', help='revert mapping')
    parser.add_argument('--version', action='version',
                        version='{} v{}'.format(__file__, __version__))
    args = parser.parse_args()

    if not os.path.isdir(args.ts_dir) or not os.path.isdir(args.ti_dir):
        print("Given path is not a directory path!")
        sys.exit(0)

    ts_files = get_all_files_from_dir(args.ts_dir, "xml", check_if_test_spec_file)
    ti_files = get_all_files_from_dir(args.ti_dir, "robot", check_if_test_impl_file)

    if args.revert:
        check_ti2ts_mapping(ti_files, ts_files)
    else:
        check_ts2ti_mapping(ts_files, ti_files)


if __name__ == "__main__":
    main()
