# Alembic-style Migrations for MongoDB

MongoDB does not support Alembic directly (it's for SQL), but you can use [migrate-mongo](https://github.com/seppevs/migrate-mongo) for versioned, scriptable migrations.

## Setup (Recommended: migrate-mongo)

1. Install migrate-mongo globally or as a dev dependency:

   ```bash
   npm install -g migrate-mongo
   # or
   yarn add --dev migrate-mongo
   ```

2. Initialize migration folder:

   ```bash
   migrate-mongo init
   # This creates a 'migrations/' folder and 'migrate-mongo-config.js'
   ```

3. Configure your MongoDB connection in `migrate-mongo-config.js`:

   ```js
   module.exports = {
     mongodb: {
       url: "mongodb://localhost:27017",
       databaseName: "crosspostme",
       options: { useNewUrlParser: true, useUnifiedTopology: true },
     },
     migrationsDir: "migrations",
     changelogCollectionName: "changelog",
   };
   ```

4. Create a migration:

   ```bash
   migrate-mongo create add-index-to-ads
   # Edit the generated file in migrations/
   ```

5. Run migrations:
   ```bash
   migrate-mongo up
   # To rollback:
   migrate-mongo down
   ```

## Example Migration Script

```js
module.exports = {
  async up(db, client) {
    await db.collection("ads").createIndex({ user_id: 1, status: 1 });
  },
  async down(db, client) {
    await db.collection("ads").dropIndex("user_id_1_status_1");
  },
};
```

## Best Practices

- Commit migration scripts to version control.
- Run migrations before deploying new code that depends on schema changes.
- Document each migration in commit messages and in the migration file.

---

**For advanced use, see the [migrate-mongo docs](https://github.com/seppevs/migrate-mongo).**
