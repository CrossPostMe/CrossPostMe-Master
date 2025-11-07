# 🚀 SUPABASE MIGRATION GUIDE

## **MongoDB → Supabase (PostgreSQL)**

---

## 📋 **MIGRATION OVERVIEW**

### **What We're Changing:**
- ❌ MongoDB Atlas → ✅ Supabase PostgreSQL
- ❌ Custom auth → ✅ Supabase Auth (optional)
- ❌ Manual user management → ✅ Built-in user system
- ❌ PyMongo queries → ✅ SQL queries via Supabase client

### **Benefits:**
- ✅ **Better scalability** - PostgreSQL handles complex queries better
- ✅ **Built-in auth** - User management out of the box
- ✅ **Real-time subscriptions** - Live data updates
- ✅ **Row Level Security** - Built-in authorization
- ✅ **Auto-generated APIs** - REST & GraphQL
- ✅ **Free tier** - Generous limits (500MB database, 2GB bandwidth)
- ✅ **Better for analytics** - SQL queries for business intelligence

---

## 🎯 **STEP 1: CREATE SUPABASE PROJECT**

### **1.1 Sign Up:**
1. Go to https://supabase.com
2. Sign in with GitHub
3. Click "New Project"
4. Fill in details:
   - **Name:** `crosspostme-production`
   - **Database Password:** Generate strong password (save it!)
   - **Region:** Choose closest to users (US East recommended)
   - **Pricing Plan:** Free (start) → Pro ($25/mo when ready)

### **1.2 Get Credentials:**

After project creation, go to **Settings → API**:

```env
SUPABASE_URL=https://toehrbdycbtgfhmrloee.supabase.co
SUPABASE_ANON_KEY=eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZWhyYmR5Y2J0Z2ZobXJsb2VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzOTkzNDMsImV4cCI6MjA3Nzk3NTM0M30.YQFbjM18MOdhNrQvzEQUP2qOOoD7sIjeBOXdhNviefE
SUPABASE_SERVICE_KEY=eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZWhyYmR5Y2J0Z2ZobXJsb2VlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTM0MywiZXhwIjoyMDc3OTc1MzQzfQ.ARJKLn2fPDOKEtbyFF18PHITPs6-RIY2xXcQGbknnx4
...
**⚠️ Important:**
- `SUPABASE_ANON_KEY` - Use in frontend (safe for public)
- `SUPABASE_SERVICE_KEY` - Use in backend only (bypasses RLS)

---

## 🗄️ **STEP 2: DATABASE SCHEMA**

### **2.1 Schema Design (PostgreSQL):**

Go to **SQL Editor** in Supabase dashboard and run this:

```sql
-- ============================================
-- CROSSPOSTME DATABASE SCHEMA
-- PostgreSQL Schema for Supabase
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),

    -- Trial & subscription
    is_active BOOLEAN DEFAULT true,
    trial_active BOOLEAN DEFAULT true,
    trial_type VARCHAR(50) DEFAULT 'free',
    trial_start_date TIMESTAMP DEFAULT NOW(),
    subscription_tier VARCHAR(50),
    subscription_status VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_date TIMESTAMP DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================
-- USER BUSINESS PROFILES
-- Separate table for better normalization
-- ============================================
CREATE TABLE user_business_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Business info
    business_name VARCHAR(255),
    business_type VARCHAR(100),
    industry VARCHAR(100),
    team_size VARCHAR(50),

    -- Marketplace data
    current_marketplaces TEXT[], -- Array of platforms
    monthly_listings VARCHAR(50),
    average_item_price VARCHAR(50),
    monthly_revenue VARCHAR(50),
    biggest_challenge TEXT,
    current_tools TEXT[],

    -- Goals
    growth_goal TEXT,
    listings_goal TEXT,

    -- Preferences
    marketing_emails BOOLEAN DEFAULT true,
    data_sharing BOOLEAN DEFAULT true,
    beta_tester BOOLEAN DEFAULT false,

    -- Attribution
    signup_source VARCHAR(100),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id)
);

-- ============================================
-- LISTINGS TABLE
-- ============================================
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Listing content
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    category VARCHAR(100),
    condition VARCHAR(50),

    -- Media
    images TEXT[], -- Array of image URLs

    -- Location
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, sold, archived

    -- Platform postings
    platforms JSONB DEFAULT '{}'::jsonb, -- {facebook: {id, url, status}, ebay: {...}}

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    sold_at TIMESTAMP
);

-- ============================================
-- BUSINESS INTELLIGENCE TABLE
-- For data mining & analytics
-- ============================================
CREATE TABLE business_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,

    timestamp TIMESTAMP DEFAULT NOW(),

    -- Indexes for fast querying
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PLATFORM CONNECTIONS TABLE
-- Track user's connected marketplace accounts
-- ============================================
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    platform VARCHAR(50) NOT NULL, -- facebook, ebay, offerup, craigslist
    platform_user_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,

    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP,

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, platform)
);

-- ============================================
-- ANALYTICS TABLE
-- Track listing performance
-- ============================================
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    platform VARCHAR(50),

    -- Metrics
    views INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0,
    messages INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,

    -- Timestamps
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(listing_id, platform, date)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_trial_active ON users(trial_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Business Profiles
CREATE INDEX idx_business_profiles_user_id ON user_business_profiles(user_id);
CREATE INDEX idx_business_profiles_industry ON user_business_profiles(industry);
CREATE INDEX idx_business_profiles_monthly_revenue ON user_business_profiles(monthly_revenue);

-- Listings
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_created_at ON listings(created_at);
CREATE INDEX idx_listings_category ON listings(category);

-- Business Intelligence
CREATE INDEX idx_bi_user_id ON business_intelligence(user_id);
CREATE INDEX idx_bi_event_type ON business_intelligence(event_type);
CREATE INDEX idx_bi_timestamp ON business_intelligence(timestamp);

-- Platform Connections
CREATE INDEX idx_platform_connections_user_id ON platform_connections(user_id);
CREATE INDEX idx_platform_connections_platform ON platform_connections(platform);

-- Analytics
CREATE INDEX idx_analytics_listing_id ON analytics(listing_id);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_date ON analytics(date);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- Users can only access their own data
-- ============================================

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_business_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Policies for business profiles
CREATE POLICY "Users can view own profile" ON user_business_profiles
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own profile" ON user_business_profiles
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Policies for listings
CREATE POLICY "Users can view own listings" ON listings
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can manage own listings" ON listings
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Policies for platform connections
CREATE POLICY "Users can view own connections" ON platform_connections
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can manage own connections" ON platform_connections
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Policies for analytics
CREATE POLICY "Users can view own analytics" ON analytics
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_profiles_updated_at BEFORE UPDATE ON user_business_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_connections_updated_at BEFORE UPDATE ON platform_connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- User stats view
CREATE VIEW user_stats AS
SELECT
    u.id,
    u.username,
    u.email,
    u.trial_type,
    u.subscription_tier,
    bp.industry,
    bp.monthly_revenue,
    bp.team_size,
    COUNT(DISTINCT l.id) as total_listings,
    COUNT(DISTINCT pc.id) as connected_platforms,
    u.created_at as signup_date
FROM users u
LEFT JOIN user_business_profiles bp ON u.id = bp.user_id
LEFT JOIN listings l ON u.id = l.user_id
LEFT JOIN platform_connections pc ON u.id = pc.user_id
GROUP BY u.id, u.username, u.email, u.trial_type, u.subscription_tier,
         bp.industry, bp.monthly_revenue, bp.team_size, u.created_at;

-- Industry breakdown view
CREATE VIEW industry_breakdown AS
SELECT
    industry,
    COUNT(*) as user_count,
    AVG(CASE
        WHEN monthly_revenue = 'under-1k' THEN 500
        WHEN monthly_revenue = '1k-5k' THEN 3000
        WHEN monthly_revenue = '5k-10k' THEN 7500
        WHEN monthly_revenue = '10k-25k' THEN 17500
        WHEN monthly_revenue = '25k-50k' THEN 37500
        WHEN monthly_revenue = '50k+' THEN 75000
        ELSE 0
    END) as avg_revenue_estimate
FROM user_business_profiles
WHERE industry IS NOT NULL
GROUP BY industry
ORDER BY user_count DESC;

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert test user
INSERT INTO users (username, email, password_hash, full_name, trial_active)
VALUES ('testuser', 'test@example.com', '$2b$12$hash', 'Test User', true)
RETURNING id;

```

Save this file as: `supabase_schema.sql`

---

## 📦 **STEP 3: INSTALL DEPENDENCIES**

```bash
cd /workspaces/CrossPostMe_MR/app/backend

# Install Supabase client
pip install supabase

# Update requirements.txt
echo "supabase>=2.0.0" >> requirements.txt
```

---

## 🔧 **STEP 4: UPDATE ENVIRONMENT VARIABLES**

**Backend `.env`:**
```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Keep these for now (migration period)
# MONGO_URL=mongodb+srv://...

# App config (keep existing)
SECRET_KEY=your-secret-key
```

**Frontend `.env`:**
```env
# Supabase (for client-side operations)
VITE_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVSUPABASE_URL=https://toehrbdycbtgfhmrloee.supabase.co
SUPABASE_ANON_KEY=eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZWhyYmR5Y2J0Z2ZobXJsb2VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzOTkzNDMsImV4cCI6MjA3Nzk3NTM0M30.YQFbjM18MOdhNrQvzEQUP2qOOoD7sIjeBOXdhNviefE
SUPABASE_SERVICE_KEY=eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvZWhyYmR5Y2J0Z2ZobXJsb2VlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTM0MywiZXhwIjoyMDc3OTc1MzQzfQ.ARJKLn2fPDOKEtbyFF18PHITPs6-RIY2xXcQGbknnx4CJ9...

# Existing vars
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## 🔄 **STEP 5: CREATE NEW DATABASE CONNECTION**

**File:** `/app/backend/supabase_db.py`

```python
"""
Supabase Database Connection
Replaces MongoDB with PostgreSQL via Supabase
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for backend

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment")

# Initialize Supabase client (singleton)
_supabase_client: Optional[Client] = None

def get_supabase() -> Client:
    """
    Get Supabase client instance (singleton pattern)

    Returns:
        Supabase client for database operations
    """
    global _supabase_client

    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    return _supabase_client

# Convenience alias
supabase = get_supabase()

# Helper functions for common operations
class SupabaseDB:
    """Wrapper class for Supabase operations"""

    def __init__(self):
        self.client = get_supabase()

    # Users
    def get_user_by_email(self, email: str):
        """Get user by email"""
        response = self.client.table("users").select("*").eq("email", email).single().execute()
        return response.data if response.data else None

    def get_user_by_username(self, username: str):
        """Get user by username"""
        response = self.client.table("users").select("*").eq("username", username).single().execute()
        return response.data if response.data else None

    def create_user(self, user_data: dict):
        """Create new user"""
        response = self.client.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None

    def update_user(self, user_id: str, updates: dict):
        """Update user"""
        response = self.client.table("users").update(updates).eq("id", user_id).execute()
        return response.data[0] if response.data else None

    # Business Profiles
    def create_business_profile(self, profile_data: dict):
        """Create business profile"""
        response = self.client.table("user_business_profiles").insert(profile_data).execute()
        return response.data[0] if response.data else None

    def get_business_profile(self, user_id: str):
        """Get business profile"""
        response = self.client.table("user_business_profiles").select("*").eq("user_id", user_id).single().execute()
        return response.data if response.data else None

    # Listings
    def create_listing(self, listing_data: dict):
        """Create listing"""
        response = self.client.table("listings").insert(listing_data).execute()
        return response.data[0] if response.data else None

    def get_user_listings(self, user_id: str):
        """Get all listings for user"""
        response = self.client.table("listings").select("*").eq("user_id", user_id).execute()
        return response.data if response.data else []

    # Business Intelligence
    def log_event(self, user_id: str, event_type: str, event_data: dict):
        """Log business intelligence event"""
        response = self.client.table("business_intelligence").insert({
            "user_id": user_id,
            "event_type": event_type,
            "event_data": event_data
        }).execute()
        return response.data[0] if response.data else None

    # Analytics queries
    def get_industry_stats(self):
        """Get industry breakdown"""
        response = self.client.table("industry_breakdown").select("*").execute()
        return response.data if response.data else []

    def get_user_stats(self):
        """Get user statistics"""
        response = self.client.table("user_stats").select("*").execute()
        return response.data if response.data else []

# Global instance
db = SupabaseDB()
```

---

## 🔄 **STEP 6: MIGRATION PLAN**

### **Phase 1: Parallel Operation (Week 1-2)**
- ✅ Keep MongoDB running
- ✅ Add Supabase alongside
- ✅ Write to both databases
- ✅ Read from MongoDB (primary)
- ✅ Test Supabase writes

### **Phase 2: Switch Reads (Week 3)**
- ✅ Read from Supabase (primary)
- ✅ Fallback to MongoDB if needed
- ✅ Monitor for issues
- ✅ Fix any data inconsistencies

### **Phase 3: Full Migration (Week 4)**
- ✅ All reads/writes to Supabase
- ✅ MongoDB in read-only mode
- ✅ Final data sync
- ✅ Remove MongoDB code

### **Phase 4: Cleanup (Week 5)**
- ✅ Remove MongoDB dependencies
- ✅ Delete MongoDB database
- ✅ Cancel MongoDB Atlas subscription
- ✅ Update documentation

---

## 📊 **COST COMPARISON**

### **MongoDB Atlas:**
- **Current:** $57/month (M10 cluster)
- **Scaling:** $200+/month for M30

### **Supabase:**
- **Free Tier:** $0/month (500MB database, 2GB bandwidth, 50K MAU)
- **Pro Tier:** $25/month (8GB database, 50GB bandwidth, 100K MAU)
- **Scaling:** $125/month (50GB+ database)

**Savings:** $32-75/month! 💰

---

## 🚀 **NEXT STEPS**

1. ✅ Create Supabase project
2. ✅ Run schema SQL
3. ✅ Install dependencies
4. ✅ Update environment variables
5. ✅ Test connection
6. ✅ Migrate one route (enhanced_signup)
7. ✅ Test thoroughly
8. ✅ Migrate remaining routes
9. ✅ Data migration script
10. ✅ Go live!

---

**Ready to start? Let's do this!** 🚀
