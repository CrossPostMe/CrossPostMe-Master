# MongoDB Migration & Backup/Restore Guide

## Migrations

- For schema migrations, use a manual approach or integrate a tool like [Mongo-Migrate](https://github.com/seppevs/migrate-mongo) or [MongoDB Migrate](https://github.com/afshinm/mongodb-migrate).
- For now, update `scripts/setup_db.py` to add new indexes or collections as needed.
- Document any schema changes in this file and in commit messages.

## Backup

- Use `scripts/backup_mongo.sh` to create a timestamped backup of your database.
- Example:
  ```bash
  ./scripts/backup_mongo.sh "mongodb://localhost:27017" crosspostme
  ```
- Backups are stored in `mongo_backups/`.

## Restore

- Use `scripts/restore_mongo.sh` to restore from a backup archive.
- Example:
  ```bash
  ./scripts/restore_mongo.sh "mongodb://localhost:27017" crosspostme mongo_backups/crosspostme_backup_YYYYMMDD_HHMMSS.gz
  ```
- The script will drop existing collections before restoring.

## Best Practices

- Run backups before any major schema or data changes.
- Store backups securely and test restores regularly.
- For production, automate backups with cron or a cloud backup service.

---

**For advanced migrations, consider integrating a migration tool and documenting each migration step.**
