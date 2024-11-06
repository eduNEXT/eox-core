#!/bin/bash

# Populate Retirement States
tutor local exec lms python manage.py lms populate_retirement_states

# Run Integration Tests
make run-integration-tests
