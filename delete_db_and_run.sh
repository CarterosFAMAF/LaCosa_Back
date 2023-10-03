#!/bin/bash

# Remove the SQLite database file
rm ./app/src/models/the_thing-db.sqlite

# Run Uvicorn with live reloading
uvicorn app.main:app --reload
