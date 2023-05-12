import os
import sys
import argparse
import unittest
import glob
import re
import shutil
import inspect

from typing import List


TESTS_TEMPLATE_FILE = "template.py.tpl"
GENERATED_TESTS_DIR = "generated_tests"


class ImportModuleTestConfig:
    def __init__(self):
        self.modules_path = ""


def parse_options(config: ImportModuleTestConfig):
    usage = f"Usage: python {__file__} [-p <modules_path>]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument(
        "-p", dest="modules_path", type=str, help="fake-bpy-module path")

    args = parser.parse_args()
    if args.modules_path:
        config.modules_path = args.modules_path


def generate_tests(config: ImportModuleTestConfig) -> list:
    # Search modules to test.
    files = glob.glob(f"{config.modules_path}/*", recursive=False)
    module_names = []
    for f in files:
        basename = os.path.basename(f)
        if basename == "py.typed":
            continue
        module_name = os.path.splitext(basename)[0]
        module_names.append(module_name)

    # Load template.
    script_dir = os.path.dirname(__file__)
    with open(f"{script_dir}/{TESTS_TEMPLATE_FILE}", "r",
              encoding="utf-8") as f:
        template_content = f.readlines()

    # Generate test codes.
    tests_dir = f"{script_dir}/{GENERATED_TESTS_DIR}"
    os.makedirs(tests_dir, exist_ok=False)
    with open(f"{tests_dir}/__init__.py", "w",   # pylint: disable=R1732
                     encoding="utf-8") as init_file:
        def replace_template_content(
                content: List[str], module_name: str) -> List[str]:
            output = []
            for line in content:
                line = re.sub(
                    r"<%% CLASS_NAME %%>",
                    "{}ImportTest".format(  # pylint: disable=C0209
                        re.sub(
                            r"_(.)",
                            lambda x: x.group(1).upper(),
                            module_name.capitalize()
                        )
                    ),
                    line)
                line = re.sub(r"<%% MODULE_NAME %%>", module_name, line)
                output.append(line)
            return output

        for mod_name in module_names:
            test_codes = replace_template_content(template_content, mod_name)
            with open(f"{tests_dir}/{mod_name}_test.py", "w",
                      encoding="utf-8") as f:
                f.writelines(test_codes)
            init_file.write(f"from . import {mod_name}_test\n")
    # Load generated modules.
    # After this time, we can delete generated test codes.
    sys.path.append(os.path.dirname(__file__))
    # pylint: disable=W0122
    exec(f"import {GENERATED_TESTS_DIR}")

    # Get test cases.
    generated_tests_package = sys.modules[GENERATED_TESTS_DIR]
    tests_modules = [
        m[1]
        for m in inspect.getmembers(generated_tests_package, inspect.ismodule)]
    test_cases = []
    for m in tests_modules:
        test_cases.extend([
            m[1]
            for m in inspect.getmembers(m, inspect.isclass)])

    # Delete generated test codes.
    shutil.rmtree(tests_dir)

    return test_cases


def run_tests(test_cases: list) -> bool:
    suite = unittest.TestSuite()
    for case in test_cases:
        suite.addTest(unittest.makeSuite(case))
    return unittest.TextTestRunner().run(suite).wasSuccessful()


def main():
    # Parse options.
    config = ImportModuleTestConfig()
    parse_options(config)

    # Add testee module.
    path = os.path.abspath(config.modules_path)
    sys.path.append(path)

    # Generate tests.
    test_cases = generate_tests(config)

    # Run tests.
    ret = run_tests(test_cases)
    sys.exit(not ret)


if __name__ == "__main__":
    main()
