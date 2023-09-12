import yaml
import os 
import logging
import pathlib
import json 
import itertools
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))
base_config = os.path.join(dir_path, 'base-generated-config.yaml')
generated_config = os.path.join(dir_path, 'generated.yml')
examples_path = os.path.join(pathlib.Path(dir_path).parent, "examples")
test_suites_path = os.path.join(pathlib.Path(dir_path).parent, "test")
main_branch = "main"


def is_valid(test_harness_path): 
  """
  Both example and test suite directories should provide following data:
  - test_entrypoint.sh
    Used to initialize test application.
  
  If shell script is not provided given entity is excluded from test harness. 
  """
  elements = [os.path.basename(name) for name in os.listdir(test_harness_path)]
  if 'test_entrypoint.sh' not in elements:
      return False 
  return True 

def get_git_tags():
  regex = "v(0|([1-9][0-9]*)\.(0|([1-9][0-9]*))\.(0|[1-9][0-9]*))|latest"
  tags = subprocess.getoutput(f"git tag -l | grep -E -w '{regex}'")
  return tags.strip().split("\n")

def list_test_suites_for_version(version):
    cmd = f"git checkout {version} && ls {test_suites_path}"
    output = subprocess.getoutput(cmd).strip()
    if "error:" in output:
        print(f"Failed to checkout or list test suites for version: {version}")
        return []
    return output.split("\n")

def app_and_name_from_path(test_harness_path): 
  test_path = str(pathlib.Path(test_harness_path).absolute())
  test_name = str(os.path.basename(test_path))  
  return test_path, test_name

def list_test_executions(example_apps, versions): 
    test_executions = []
    for app, version in itertools.product(example_apps, versions):
        if not is_valid(app):
            print(f"---\nApp: {app}\nwill not be executed.\ntest_entrypoint.sh is missing.\n---")
            continue

        suites_for_version = list_test_suites_for_version(version)
        for suite in suites_for_version:
            suite_path = os.path.join(test_suites_path, suite)
            if not os.path.exists(suite_path) or not is_valid(suite_path):
                print(f"---\nTest Suite: {suite}\nwill not be executed.\ntest_entrypoint.sh is missing.\n---")
                continue

            app_path, app_name = app_and_name_from_path(app)
            _, suite_name = app_and_name_from_path(suite_path)

            new_example = {
                'example-app-path': app_path, 'test-suite-name': suite_name,
                'example-app-name': app_name, 'test-suite-path': suite_path,
                'bb-version': version,
                'name': f'{app_name} ({suite_name} test suite , version: {version})'
            }
            test_executions.append({"test-example": new_example})
    return test_executions

with open(base_config) as f:
    circle_config = yaml.safe_load(f)
    
    available_examples = [name for name in pathlib.Path(examples_path).iterdir() if os.path.isdir(name)]
    available_versions = get_git_tags()
    available_versions.append(main_branch)
    circle_config['workflows']['test_everything']['jobs'] = list_test_executions(available_examples, available_versions)

    with open(generated_config, "w") as w: 
      yaml.dump(circle_config, w, default_flow_style=False)
