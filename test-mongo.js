// test-mongo.js
// Usage:
//   node test-mongo.js "<MONGO_URI>"
// or:
//   $env:MONGO_URI="<MONGO_URI>"; node test-mongo.js

const { MongoClient } = require('mongodb');

const uri = process.argv[2] || process.env.MONGO_URI;
if (!uri) {
  console.error("Usage: node test-mongo.js \"<MONGO_URI>\"");
  process.exit(2);
}

(async () => {
  try {
    const client = new MongoClient(uri, { serverSelectionTimeoutMS: 5000 });
    await client.connect();
    const ping = await client.db().admin().ping();
    console.log("PING OK:", JSON.stringify(ping));
    await client.close();
    process.exit(0);
  } catch (err) {
    console.error("CONNECTION ERROR:");
    console.error(err && err.stack ? err.stack : err);
    process.exit(1);
  }
})();
