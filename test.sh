#!/bin/bash

# Define the path to the SQLite database file
DB_FILE="./app/src/models/test-the_thing-db.sqlite"

# Check if the database file exists
if [ -f "$DB_FILE" ]; then
  # If the database file exists, remove it
  echo "Removing the database file: $DB_FILE"
  rm "$DB_FILE"
fi

# Run pytest
echo "Running pytest..."
pytest