# 🚀 SUPABASE MIGRATION GUIDE
## **MongoDB → Supabase (PostgreSQL) Migration**

**Date:** November 5, 2025
**Status:** Ready to Implement
**Benefit:** Free tier, better performance, built-in auth, real-time subscriptions

---

## 🎯 WHY SWITCH TO SUPABASE?

### **Advantages Over MongoDB:**

| Feature | MongoDB Atlas | Supabase | Winner |
|---------|---------------|----------|--------|
| **Free Tier** | 512MB storage | 500MB database + 1GB file storage | ⚖️ Tie |
| **Built-in Auth** | ❌ Need separate | ✅ Included | 🏆 Supabase |
| **Real-time** | ❌ Separate | ✅ Built-in | 🏆 Supabase |
| **SQL Support** | ❌ NoSQL only | ✅ PostgreSQL | 🏆 Supabase |
| **File Storage** | ❌ Separate (S3) | ✅ Built-in | 🏆 Supabase |
| **REST API** | ❌ Need to build | ✅ Auto-generated | 🏆 Supabase |
| **Edge Functions** | ❌ No | ✅ Yes | 🏆 Supabase |
| **Dashboard** | ✅ Good | ✅ Excellent | 🏆 Supabase |
| **Pricing** | $57/mo (M10) | $25/mo (Pro) | 🏆 Supabase |

### **Cost Comparison:**

**Year 1 (25K users):**
- MongoDB Atlas: ~$684/year (M10 cluster)
- Supabase: $0 (Free tier) → $300/year (Pro tier after 6 months)
- **Savings:** $384/year

---

## 📊 DATABASE SCHEMA MIGRATION

### **Current MongoDB Collections → Supabase Tables**

#### **1. Users Collection → users table**

**MongoDB:**
```javascript
{
  _id: ObjectId("..."),
  email: "user@example.com",
  password_hash: "hashed_password",
  name: "John Doe",
  subscription_plan: "proseller",
  created_at: ISODate("2025-11-05"),
  stripe_customer_id: "cus_..."
}
```

**Supabase SQL:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  subscription_plan TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own data
CREATE POLICY "Users can read own data" ON users
  FOR SELECT USING (auth.uid() = id);
```

---

#### **2. Ads Collection → ads table**

**MongoDB:**
```javascript
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),
  title: "iPhone 13 Pro",
  description: "Excellent condition...",
  price: 650,
  images: ["url1.jpg", "url2.jpg"],
  platforms: ["facebook", "ebay"],
  status: "active",
  created_at: ISODate("2025-11-05")
}
```

**Supabase SQL:**
```sql
CREATE TABLE ads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  price DECIMAL(10, 2),
  images TEXT[], -- Array of image URLs
  platforms TEXT[], -- Array of platform names
  status TEXT DEFAULT 'draft',
  category TEXT,
  location TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE ads ENABLE ROW LEVEL SECURITY;

-- Policy: Users can CRUD their own ads
CREATE POLICY "Users can manage own ads" ON ads
  FOR ALL USING (auth.uid() = user_id);

-- Index for performance
CREATE INDEX idx_ads_user_id ON ads(user_id);
CREATE INDEX idx_ads_status ON ads(status);
```

---

#### **3. Leads Collection → leads table**

**MongoDB:**
```javascript
{
  _id: ObjectId("..."),
  ad_id: ObjectId("..."),
  user_id: ObjectId("..."),
  name: "Jane Buyer",
  email: "jane@example.com",
  message: "Is this still available?",
  platform: "facebook",
  created_at: ISODate("2025-11-05")
}
```

**Supabase SQL:**
```sql
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ad_id UUID REFERENCES ads(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT,
  email TEXT,
  phone TEXT,
  message TEXT,
  offer_amount DECIMAL(10, 2),
  platform TEXT NOT NULL,
  status TEXT DEFAULT 'new',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY "Users can manage own leads" ON leads
  FOR ALL USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_leads_user_id ON leads(user_id);
CREATE INDEX idx_leads_ad_id ON leads(ad_id);
CREATE INDEX idx_leads_status ON leads(status);
```

---

#### **4. Platform Connections → platform_connections table**

**Supabase SQL:**
```sql
CREATE TABLE platform_connections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, platform)
);

-- Enable RLS
ALTER TABLE platform_connections ENABLE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY "Users can manage own connections" ON platform_connections
  FOR ALL USING (auth.uid() = user_id);
```

---

## 🔧 BACKEND CODE MIGRATION

### **Install Supabase Python Client:**

```bash
pip install supabase
```

**Update requirements.txt:**
```txt
supabase==2.0.0
postgrest-py==0.13.0
```

---

### **Database Connection (db.py)**

**OLD (MongoDB):**
```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

MONGODB_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGODB_URI, server_api=ServerApi('1'))
db = client.crosspostme
```

**NEW (Supabase):**
```python
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# For client operations (respects RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# For admin operations (bypasses RLS)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
```

---

### **User Operations**

**OLD (MongoDB):**
```python
# Create user
user = await db.users.insert_one({
    "email": email,
    "password_hash": hashed_password,
    "created_at": datetime.utcnow()
})

# Find user
user = await db.users.find_one({"email": email})

# Update user
await db.users.update_one(
    {"_id": ObjectId(user_id)},
    {"$set": {"subscription_plan": "proseller"}}
)
```

**NEW (Supabase):**
```python
# Create user (use Supabase Auth)
response = supabase.auth.sign_up({
    "email": email,
    "password": password,
    "options": {
        "data": {
            "name": name
        }
    }
})

# Find user
response = supabase.table("users").select("*").eq("email", email).execute()
user = response.data[0] if response.data else None

# Update user
response = supabase.table("users").update({
    "subscription_plan": "proseller"
}).eq("id", user_id).execute()
```

---

### **Ad Operations**

**OLD (MongoDB):**
```python
# Create ad
ad = await db.ads.insert_one({
    "user_id": ObjectId(user_id),
    "title": title,
    "price": price,
    "images": images,
    "created_at": datetime.utcnow()
})

# Get user's ads
ads = await db.ads.find({"user_id": ObjectId(user_id)}).to_list(100)

# Update ad
await db.ads.update_one(
    {"_id": ObjectId(ad_id)},
    {"$set": {"status": "sold"}}
)
```

**NEW (Supabase):**
```python
# Create ad
response = supabase.table("ads").insert({
    "user_id": user_id,
    "title": title,
    "price": price,
    "images": images
}).execute()

# Get user's ads
response = supabase.table("ads").select("*").eq("user_id", user_id).execute()
ads = response.data

# Update ad
response = supabase.table("ads").update({
    "status": "sold"
}).eq("id", ad_id).execute()
```

---

### **Lead Operations**

**OLD (MongoDB):**
```python
# Create lead
lead = await db.leads.insert_one({
    "ad_id": ObjectId(ad_id),
    "user_id": ObjectId(user_id),
    "name": name,
    "message": message,
    "created_at": datetime.utcnow()
})

# Get leads with ad info
pipeline = [
    {"$match": {"user_id": ObjectId(user_id)}},
    {"$lookup": {
        "from": "ads",
        "localField": "ad_id",
        "foreignField": "_id",
        "as": "ad"
    }}
]
leads = await db.leads.aggregate(pipeline).to_list(100)
```

**NEW (Supabase):**
```python
# Create lead
response = supabase.table("leads").insert({
    "ad_id": ad_id,
    "user_id": user_id,
    "name": name,
    "message": message
}).execute()

# Get leads with ad info (JOIN)
response = supabase.table("leads").select(
    "*, ads(title, price, images)"
).eq("user_id", user_id).execute()
leads = response.data
```

---

## 🔐 AUTHENTICATION MIGRATION

### **Supabase Auth Integration**

**Benefits:**
- ✅ Email/password authentication
- ✅ OAuth (Google, Facebook, GitHub, etc.)
- ✅ Magic links
- ✅ JWT tokens
- ✅ Session management
- ✅ Password reset

**Backend Integration:**
```python
from fastapi import Depends, HTTPException, Header
from supabase import Client

async def get_current_user(
    authorization: str = Header(...),
    supabase: Client = Depends(get_supabase)
):
    """Get current authenticated user from JWT token"""
    try:
        # Extract token
        token = authorization.replace("Bearer ", "")

        # Verify token
        user = supabase.auth.get_user(token)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user

    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Use in routes
@app.get("/api/ads")
async def get_ads(current_user = Depends(get_current_user)):
    user_id = current_user.user.id
    response = supabase.table("ads").select("*").eq("user_id", user_id).execute()
    return response.data
```

---

## 📁 FILE STORAGE (BONUS!)

Supabase includes free file storage! Perfect for ad images.

**Upload Image:**
```python
# Upload to Supabase Storage
with open("image.jpg", "rb") as f:
    response = supabase.storage.from_("ad-images").upload(
        f"ads/{ad_id}/image1.jpg",
        f,
        {"content-type": "image/jpeg"}
    )

# Get public URL
url = supabase.storage.from_("ad-images").get_public_url(
    f"ads/{ad_id}/image1.jpg"
)
```

**Create Storage Bucket:**
```sql
-- In Supabase Dashboard → Storage
-- Create bucket: ad-images
-- Set public: true
-- Add RLS policy
```

---

## ⚡ REAL-TIME FEATURES

Get instant updates when data changes!

**Frontend (JavaScript):**
```javascript
// Subscribe to new leads
const channel = supabase
  .channel('leads-channel')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'leads',
      filter: `user_id=eq.${userId}`
    },
    (payload) => {
      console.log('New lead!', payload.new)
      // Show notification
      showNotification('New lead received!')
    }
  )
  .subscribe()
```

---

## 🚀 MIGRATION STEPS

### **Phase 1: Setup (1 hour)**

1. **Create Supabase Project:**
   - Go to https://supabase.com
   - Click "New Project"
   - Choose region (Oregon for US West)
   - Set database password (save it!)

2. **Get Credentials:**
   - Go to Settings → API
   - Copy:
     - Project URL
     - anon/public key
     - service_role key (keep secret!)

3. **Run SQL Schema:**
   - Go to SQL Editor
   - Paste all CREATE TABLE statements
   - Click "Run"

---

### **Phase 2: Code Migration (2-4 hours)**

1. **Install Supabase client:**
   ```bash
   pip install supabase
   ```

2. **Update environment variables:**
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

3. **Replace MongoDB code:**
   - Update db.py
   - Update auth.py
   - Update all model files
   - Update API routes

4. **Test locally:**
   ```bash
   python -m pytest tests/
   ```

---

### **Phase 3: Data Migration (1-2 hours)**

**Export from MongoDB:**
```bash
mongoexport --uri="mongodb+srv://..." --collection=users --out=users.json
mongoexport --uri="mongodb+srv://..." --collection=ads --out=ads.json
mongoexport --uri="mongodb+srv://..." --collection=leads --out=leads.json
```

**Import to Supabase:**
```python
import json
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Import users
with open('users.json') as f:
    users = [json.loads(line) for line in f]
    for user in users:
        # Transform MongoDB format to Supabase
        supabase.table('users').insert({
            'email': user['email'],
            'name': user.get('name'),
            'subscription_plan': user.get('subscription_plan', 'free'),
            'created_at': user['created_at']
        }).execute()

# Repeat for ads and leads
```

---

### **Phase 4: Deploy (30 minutes)**

1. **Update Render environment variables**
2. **Deploy backend**
3. **Test production**
4. **Monitor for errors**

---

## 💰 COST SAVINGS

| Service | MongoDB | Supabase | Savings |
|---------|---------|----------|---------|
| **Month 1-6** | $57/mo | $0 (Free) | $342 |
| **Month 7-12** | $57/mo | $25/mo | $192 |
| **Year 1 Total** | $684 | $150 | **$534** |
| **Year 2 Total** | $684 | $300 | **$384** |

---

## ✅ CHECKLIST

### **Before Migration:**
- [ ] Create Supabase project
- [ ] Set up database schema
- [ ] Test locally with sample data
- [ ] Update all environment variables

### **During Migration:**
- [ ] Backup MongoDB data
- [ ] Export all collections
- [ ] Transform data format
- [ ] Import to Supabase
- [ ] Verify data integrity

### **After Migration:**
- [ ] Test all API endpoints
- [ ] Test authentication
- [ ] Test file uploads
- [ ] Monitor performance
- [ ] Update documentation

---

## 🎉 READY TO MIGRATE?

**Let's do this!** Supabase will give you:
- ✅ Better performance
- ✅ Lower costs
- ✅ Built-in auth
- ✅ Real-time features
- ✅ File storage
- ✅ Better developer experience

**Want me to start the migration?** Just say the word! 🚀
