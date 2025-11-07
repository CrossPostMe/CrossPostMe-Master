#!/bin/bash
# Manual MongoDB backup script
# Dumps all collections in the configured database to a timestamped archive
# Usage: ./backup_mongo.sh <mongo_url> <db_name>

MONGO_URL=${1:-mongodb://localhost:27017}
DB_NAME=${2:-crosspostme}
TS=$(date +%Y%m%d_%H%M%S)
OUT_DIR="mongo_backups"
ARCHIVE="$OUT_DIR/${DB_NAME}_backup_$TS.gz"

mkdir -p "$OUT_DIR"

echo "Backing up $DB_NAME from $MONGO_URL to $ARCHIVE..."
mongodump --uri="$MONGO_URL" --db="$DB_NAME" --archive="$ARCHIVE" --gzip

if [ $? -eq 0 ]; then
  echo "Backup successful: $ARCHIVE"
else
  echo "Backup failed!"
fi
