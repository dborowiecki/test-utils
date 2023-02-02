#!/bin/bash
echo "$TEMPLATE_CONTENT" > .circleci/base-generated-config.yaml
echo "$SCRIPT_CONTENT" > .circleci/generate-config.py