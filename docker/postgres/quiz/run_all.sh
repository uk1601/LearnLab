#!/bin/bash

# Script to run all quiz sample data population scripts in order

DB_NAME="learnlab"

echo "Starting quiz sample data population..."

# Function to run SQL file and check for errors
run_sql_file() {
    echo "Running $1..."
    psql -d $DB_NAME -f "$1"
    if [ $? -ne 0 ]; then
        echo "Error executing $1"
        exit 1
    fi
}

# Run all SQL files in order
for file in $(ls [0-9][0-9]_*.sql | sort); do
    run_sql_file "$file"
done

echo "Quiz sample data population completed successfully!"