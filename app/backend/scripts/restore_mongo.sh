#!/bin/bash
# Manual MongoDB restore script
# Restores all collections from a backup archive
# Usage: ./restore_mongo.sh <mongo_url> <db_name> <archive_path>

MONGO_URL=${1:-mongodb://localhost:27017}
DB_NAME=${2:-crosspostme}
ARCHIVE=${3}

if [ -z "$ARCHIVE" ]; then
  echo "Usage: $0 <mongo_url> <db_name> <archive_path>"
  exit 1
fi

echo "Restoring $DB_NAME from $ARCHIVE to $MONGO_URL..."
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" --archive="$ARCHIVE" --gzip --drop

if [ $? -eq 0 ]; then
  echo "Restore successful."
else
  echo "Restore failed!"
fi
