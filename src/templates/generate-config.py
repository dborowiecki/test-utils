import yaml
import os 
import logging
import pathlib
import json 
import itertools


dir_path = os.path.dirname(os.path.realpath(__file__))
base_config = os.path.join(dir_path, 'base-generated-config.yaml')
generated_config = os.path.join(dir_path, 'generated.yml')
examples_path = os.path.join(pathlib.Path(dir_path).parent, "examples")
test_suites_path = os.path.join(pathlib.Path(dir_path).parent, "test")


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


def app_and_name_from_path(test_harness_path): 
    test_path = str(pathlib.Path(test_harness_path).absolute())
    test_name = str(os.path.basename(test_path))  
    return test_path, test_name

def list_test_executions(example_apps, test_suites): 
  # Test are executed for all cancidate applications tested against all test suites
  test_executions = []
  for element in itertools.product(example_apps, test_suites):
    app, suite = element 
    if not (is_valid(app) and is_valid(suite)):
      print(F'---\nTest harness for:\n\tApp: {app}\n\tTest Suite: {suite}"\nwill not be executed.\ntest_entrypoint.sh is missing.\n---')
      continue

    app_path, app_name = app_and_name_from_path(app)
    suite_path, suite_name = app_and_name_from_path(suite)

    new_example = {
      'example-app-path': app_path, 'test-suite-name': suite_name, 
      'example-app-name': app_name, 'test-suite-path': suite_path, 
    }
    test_executions.append({F"test-example": new_example})
  return test_executions


with open(base_config) as f:
    circle_config = yaml.safe_load(f)
    
    available_examples = [name for name in pathlib.Path(examples_path).iterdir() if os.path.isdir(name)]
    available_test_suites = [name for name in pathlib.Path(test_suites_path).iterdir() if os.path.isdir(name)]
    circle_config['workflows']['test_everything']['jobs'] = list_test_executions(available_examples, available_test_suites)

    with open(generated_config, "w") as w: 
      yaml.dump(circle_config, w, default_flow_style=False)