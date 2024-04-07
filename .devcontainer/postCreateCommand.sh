#!/bin/bash
poetry install --no-root
gh auth login --with-token < .ghtoken
