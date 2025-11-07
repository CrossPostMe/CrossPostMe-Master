# 🚨 SUPABASE SETUP - ACTION REQUIRED

## ✅ What's Done:
- Environment variables configured
- SQL schema ready with security fixes
- All security warnings addressed:
  - ✅ RLS enabled on business_intelligence table
  - ✅ Function search_path set (security fix)
  - ✅ Views use security_invoker (not security_definer)

## ❌ What's Blocking:
**401 "Invalid API key" error**

This means **one of two things**:

### **Option 1: Schema Not Run Yet** (Most Likely)
You need to manually run the SQL in Supabase dashboard.

### **Option 2: Wrong API Keys**
The keys in the migration doc might be examples, not real keys.

---

## 🎯 **SOLUTION - DO THIS NOW:**

### **Step 1: Verify Project Exists**

1. Go to: https://supabase.com/dashboard
2. Look for project named: **toehrbdycbtgfhmrloee**
3. If it doesn't exist → Create new project
4. If it exists → Continue to Step 2

---

### **Step 2: Get REAL API Keys**

1. Open your project: https://supabase.com/dashboard/project/toehrbdycbtgfhmrloee
2. Click **Settings** (gear icon, bottom left)
3. Click **API**
4. Copy these values:

```
Project URL: https://_____.supabase.co
anon public: eyJ_____
service_role: eyJ_____ (click "Reveal" button)
```

---

### **Step 3: Update Environment Variables**

Edit `/app/backend/.env`:

```env
SUPABASE_URL=https://_____.supabase.co  # Your real URL
SUPABASE_ANON_KEY=eyJ_____  # Your real anon key
SUPABASE_SERVICE_KEY=eyJ_____  # Your real service key (secret!)
```

---

### **Step 4: Run SQL Schema**

1. In Supabase dashboard → **SQL Editor**
2. Click **New Query**
3. Copy ALL of `supabase_schema.sql`
4. Paste and click **Run** ▶️
5. Should see: "Success. No rows returned"

---

### **Step 5: Test Connection**

```bash
cd /workspaces/CrossPostMe_MR/app/backend
python3 test_supabase.py
```

Should see:
```
✅ Supabase client initialized
✅ Database query successful
✅ All tables exist
```

---

## 🔍 **CURRENT STATUS:**

| Item | Status |
|------|--------|
| Supabase project | ❓ Unknown (check dashboard) |
| API keys | ⚠️ Might be examples, not real |
| SQL schema | ⏳ Needs to be run manually |
| Connection test | ❌ Failing (401 error) |

---

## 💡 **QUICK CHECK:**

Run this to see current status:
```bash
python3 check_supabase_creds.py
```

---

## 📋 **IF PROJECT DOESN'T EXIST:**

Create a new Supabase project:

1. Go to: https://supabase.com/dashboard
2. Click "New Project"
3. Name: `crosspostme-production`
4. Database Password: Generate and SAVE IT!
5. Region: US East (or closest to you)
6. Click "Create Project"
7. Wait 2-3 minutes for provisioning
8. Get API keys from Settings → API
9. Update `.env` files
10. Run SQL schema
11. Test connection

---

## 🚀 **ONCE KEYS ARE CORRECT:**

Everything else is ready:
- ✅ SQL schema (security-fixed)
- ✅ Database wrapper (`supabase_db.py`)
- ✅ Test scripts
- ✅ Migration docs

Just need valid API keys!

---

## 🆘 **NEED HELP?**

The credentials in `SUPABASE_MIGRATION.md` might be placeholder examples.

Get the REAL keys from your Supabase dashboard:
https://supabase.com/dashboard/project/YOUR-PROJECT/settings/api

Then update:
- `/app/backend/.env`
- `/app/frontend/.env`

And run the SQL schema!
