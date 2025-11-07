# 🌐 CROSSPOSTME - PLATFORM INTEGRATION MASTER PLAN

**Date:** November 5, 2025
**Status:** Expansion Phase
**Platforms:** 7+ Marketplace Integrations

---

## 📊 PLATFORM OVERVIEW

| Platform | Integration Type | Fee | API Status | Priority | Avg GMV |
|----------|-----------------|-----|------------|----------|---------|
| **eBay** | API (OAuth) | 12.9% | ✅ Complete | P0 | $18B/yr |
| **Facebook Marketplace** | API (OAuth) | 5% | ✅ Complete | P0 | $20B/yr |
| **Craigslist** | Automation | 0% | ✅ Complete | P0 | $4B/yr |
| **OfferUp** | Automation | 12.9% | ✅ Complete | P0 | $8B/yr |
| **Nextdoor** | Automation/API | 0% | 🔄 NEW | P1 | $2B/yr |
| **Etsy** | API (OAuth) | 6.5% | 🔄 NEW | P1 | $13B/yr |
| **Poshmark** | Automation | 20% | 🔄 NEW | P2 | $2B/yr |
| **Custom API** | API Keys | Varies | ✅ Ready | P1 | N/A |
| **Manual Mode** | AI Generation | N/A | ✅ Ready | P0 | N/A |
| **CSV Bulk Upload** | Team/Agency | N/A | ✅ Ready | P1 | N/A |

**Total Platform GMV:** $67B+ annually (expanded from $50B)

---

## 🔐 PLATFORM API REQUIREMENTS & TERMS OF SERVICE

### **1. eBay** ✅ COMPLETE

#### **API Access:**
- **Type:** Trading API (REST/XML)
- **OAuth:** 2.0 (3-legged)
- **Documentation:** https://developer.ebay.com/docs

#### **Required Credentials:**
```env
EBAY_APP_ID=your_app_id
EBAY_DEV_ID=your_dev_id
EBAY_CERT_ID=your_cert_id
EBAY_REDIRECT_URI=https://yourdomain.com/oauth/ebay/callback
```

#### **Rate Limits:**
- **Sandbox:** 5,000 calls/day
- **Production:** Based on application tier
  - Basic: 5,000 calls/day
  - Advanced: 1,500,000 calls/day

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Automated listing creation
- Bulk uploads
- Price updates
- Inventory sync
- Order management

❌ **Prohibited:**
- Scraping without API
- Bid manipulation
- Fake listings
- Duplicate listings (same item multiple times)
- Misleading descriptions

#### **Safeguards Implemented:**
```python
# Rate limiting
@rate_limit(calls=5000, period=86400)  # 5000/day

# Duplicate detection
def check_duplicate(title, price, user_id):
    existing = db.listings.find_one({
        'user_id': user_id,
        'title': title,
        'price': price,
        'status': 'active'
    })
    if existing:
        raise ValueError("Duplicate listing detected")

# Content validation
def validate_listing(data):
    if len(data['title']) > 80:
        raise ValueError("eBay title max 80 chars")
    if 'prohibited_keywords' in data['description']:
        raise ValueError("Prohibited content detected")
```

---

### **2. Facebook Marketplace** ✅ COMPLETE

#### **API Access:**
- **Type:** Graph API
- **OAuth:** 2.0
- **Documentation:** https://developers.facebook.com/docs/marketplace

#### **Required Credentials:**
```env
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=https://yourdomain.com/oauth/facebook/callback
```

#### **Required Permissions:**
- `pages_manage_metadata`
- `pages_read_engagement`
- `pages_show_list`
- `business_management`
- `catalog_management`

#### **Rate Limits:**
- **App-level:** 200 calls/hour/user
- **Page-level:** Based on usage tier

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Legitimate business listings
- Accurate descriptions
- Real photos
- One listing per item

❌ **Prohibited:**
- Adult content
- Weapons/drugs
- Counterfeit items
- Services (in most categories)
- Multi-level marketing
- Duplicate listings

#### **Safeguards Implemented:**
```python
# Category validation
ALLOWED_CATEGORIES = [
    'Vehicles', 'Property Rentals', 'Apparel',
    'Electronics', 'Home & Garden', 'Toys & Games',
    'Sporting Goods', 'Hobbies', 'Entertainment'
]

def validate_facebook_listing(data):
    # Content filter
    prohibited_words = ['replica', 'fake', 'counterfeit', 'mlm']
    if any(word in data['description'].lower() for word in prohibited_words):
        raise ValueError("Prohibited content")

    # Image validation
    if len(data['images']) < 1:
        raise ValueError("At least 1 image required")

    # Price validation
    if data['price'] <= 0 or data['price'] > 500000:
        raise ValueError("Price must be $0.01 - $500,000")
```

---

### **3. Craigslist** ✅ ASSISTED WORKFLOW (Compliant!)

#### **API Access:**
- **Type:** No official API
- **Method:** ✅ **ASSISTED WORKFLOW** (User-guided, not automated)
- **Documentation:** User terms: https://www.craigslist.org/about/terms.of.use

#### **How It Works (100% Compliant):**
```
User Action Required at Each Step:
1. User clicks "Post to Craigslist"
2. System opens Craigslist in popup/new tab
3. System PRE-FILLS form with listing data
4. ⚠️ USER REVIEWS and clicks "Continue" in Craigslist
5. ⚠️ USER completes CAPTCHA (if required)
6. ⚠️ USER clicks "Publish" button themselves
7. System detects success and saves listing ID
```

**Why This is Compliant:**
- ✅ User is in control at every step
- ✅ No automated posting/clicking
- ✅ We're just an "assistant" that fills forms
- ✅ User handles CAPTCHAs and verification
- ✅ User makes final publish decision
- ✅ Similar to password manager auto-fill

#### **Rate Limits:**
- **Manual:** ~48 posts per account per day
- **Per city:** Different limits per metro area
- **Phone verification:** Required for certain categories

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Personal sales
- Local transactions
- One post per item/city
- Repost every 48 hours (not sooner)
- ✅ **Assistive tools** (form fillers, helpers)

❌ **Prohibited:**
- Commercial spam
- Duplicate posts
- Cross-posting to multiple cities excessively
- Adult services
- Weapons/drugs
- ✅ **Fully automated bots** (we're NOT doing this!)

#### **Safeguards Implemented:**
```python
# Posting frequency control
def check_craigslist_rate_limit(user_id, city):
    last_post = db.craigslist_posts.find_one({
        'user_id': user_id,
        'city': city,
        'timestamp': {'$gte': datetime.now() - timedelta(hours=48)}
    })
    if last_post:
        raise ValueError("Wait 48 hours between posts in same city")

# City limit
MAX_CITIES_PER_POST = 3

def validate_craigslist_post(data):
    if len(data['cities']) > MAX_CITIES_PER_POST:
        raise ValueError(f"Maximum {MAX_CITIES_PER_POST} cities per post")

    # Phone verification check
    if data['category'] in ['jobs', 'services', 'housing']:
        if not user.phone_verified:
            raise ValueError("Phone verification required for this category")
```

---

### **4. OfferUp** ✅ COMPLETE (Automation)

#### **API Access:**
- **Type:** No official public API
- **Method:** Browser automation
- **Documentation:** Terms: https://offerup.com/terms

#### **Required Information:**
```env
OFFERUP_EMAIL=user_email
OFFERUP_PASSWORD=encrypted_password
OFFERUP_PHONE=verified_phone
```

#### **Rate Limits:**
- **Listings:** No hard limit, but suspicious activity flagged
- **Photos:** 12 max per listing
- **Bump:** Once per 24 hours

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Personal item sales
- Local transactions
- Legitimate business accounts
- Shipping available

❌ **Prohibited:**
- Stolen goods
- Counterfeit items
- Prohibited items (weapons, drugs, adult)
- Fake accounts
- Spamming

#### **Safeguards Implemented:**
```python
# Rate limiting
@rate_limit(calls=50, period=86400)  # 50 posts/day max

def validate_offerup_listing(data):
    # Image limit
    if len(data['images']) > 12:
        raise ValueError("OfferUp allows max 12 images")

    # Location validation
    if not data.get('location'):
        raise ValueError("Location required for OfferUp")

    # Price validation
    if data['price'] < 1:
        raise ValueError("OfferUp requires minimum $1")
```

---

### **5. Nextdoor** 🔄 NEW INTEGRATION

#### **API Access:**
- **Type:** Business API (Limited access)
- **OAuth:** 2.0 (invitation only)
- **Documentation:** https://business.nextdoor.com/api

#### **Required Credentials:**
```env
NEXTDOOR_CLIENT_ID=your_client_id
NEXTDOOR_CLIENT_SECRET=your_client_secret
NEXTDOOR_API_KEY=your_api_key
```

#### **API Application Process:**
1. Apply at: https://business.nextdoor.com/api/apply
2. Wait for approval (2-4 weeks)
3. Review process based on use case
4. Restricted to verified businesses

#### **Alternative: Automation Method**
```env
NEXTDOOR_EMAIL=user_email
NEXTDOOR_PASSWORD=encrypted_password
NEXTDOOR_ADDRESS=verified_address
```

#### **Rate Limits:**
- **API:** TBD (invitation only)
- **Manual:** ~20 posts per week recommended
- **Neighborhoods:** Post to your own + adjacent

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Local sales (nearby neighborhoods)
- Service offerings (verified businesses)
- Garage sales
- Free items
- Recommendations

❌ **Prohibited:**
- Commercial spam
- Multi-level marketing
- Adult content
- Weapons/drugs
- Posting to too many neighborhoods
- Fake accounts

#### **Safeguards Implemented:**
```python
# Neighborhood limiting
MAX_NEIGHBORHOODS = 5

def validate_nextdoor_post(user, data):
    # Verify user address
    if not user.address_verified:
        raise ValueError("Must verify address to post on Nextdoor")

    # Check neighborhood limit
    if len(data['neighborhoods']) > MAX_NEIGHBORHOODS:
        raise ValueError(f"Maximum {MAX_NEIGHBORHOODS} neighborhoods")

    # Posting frequency
    recent_posts = count_posts_last_7_days(user.id, 'nextdoor')
    if recent_posts >= 20:
        raise ValueError("Nextdoor weekly limit reached (20 posts)")

    # Local validation
    if data.get('price', 0) > 10000:
        return "High-value items may require business verification"
```

---

### **6. Etsy** 🔄 NEW INTEGRATION

#### **API Access:**
- **Type:** Open API v3
- **OAuth:** 2.0
- **Documentation:** https://developers.etsy.com/documentation

#### **Required Credentials:**
```env
ETSY_API_KEY=your_keystring
ETSY_SHARED_SECRET=your_secret
ETSY_OAUTH_CONSUMER_KEY=your_consumer_key
ETSY_OAUTH_CONSUMER_SECRET=your_consumer_secret
```

#### **Rate Limits:**
- **API calls:** 10,000 per day per application
- **Burst:** 10 per second
- **Shop limits:** Based on shop tier

#### **Etsy Shop Requirements:**
- Must have active Etsy shop
- Shop must be in good standing
- Listings must follow Etsy policies

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Handmade items
- Vintage items (20+ years old)
- Craft supplies
- Digital downloads
- Made-to-order

❌ **Prohibited:**
- Reselling commercial items
- Drop shipping
- Mass-produced items
- Prohibited items (weapons, drugs, etc.)
- Items you didn't make/design/curate
- Services (except Etsy Pattern)

#### **Safeguards Implemented:**
```python
# Category validation
ETSY_ALLOWED_TYPES = ['handmade', 'vintage', 'supplies']

def validate_etsy_listing(user, data):
    # Shop verification
    if not user.etsy_shop_id:
        raise ValueError("Must connect Etsy shop first")

    # Category check
    if data['type'] not in ETSY_ALLOWED_TYPES:
        raise ValueError(f"Etsy only allows: {', '.join(ETSY_ALLOWED_TYPES)}")

    # Vintage validation
    if data['type'] == 'vintage':
        if not data.get('made_year') or (2025 - data['made_year']) < 20:
            raise ValueError("Vintage items must be 20+ years old")

    # Handmade validation
    if data['type'] == 'handmade':
        if not data.get('who_made'):
            data['who_made'] = 'i_did'  # Must specify creator

    # Image requirements
    if len(data['images']) < 1 or len(data['images']) > 10:
        raise ValueError("Etsy requires 1-10 images")

    # Title length
    if len(data['title']) > 140:
        raise ValueError("Etsy title max 140 characters")
```

---

### **7. Poshmark** 🔄 NEW INTEGRATION

#### **API Access:**
- **Type:** No official public API
- **Method:** Browser automation required
- **Documentation:** Terms: https://poshmark.com/terms

#### **Required Information:**
```env
POSHMARK_EMAIL=user_email
POSHMARK_PASSWORD=encrypted_password
```

#### **Rate Limits:**
- **Listings:** ~100 per day (soft limit)
- **Shares:** 10,000 per day
- **Follows:** 10,000 per day
- **Comments:** Varies, anti-spam detection

#### **Poshmark Requirements:**
- Fashion/home decor focus
- Photos required (cover + up to 15 more)
- Must follow community guidelines

#### **Terms of Service Key Points:**
✅ **Allowed:**
- Women's fashion
- Men's fashion
- Kids' fashion
- Home decor
- Beauty products
- Pet accessories
- New with tags (NWT)
- Gently used items

❌ **Prohibited:**
- Counterfeit items
- Replica/knockoffs
- Used cosmetics/intimates (most)
- Recalled items
- Electronics (mostly)
- Live animals
- Weapons
- Drug paraphernalia

#### **Safeguards Implemented:**
```python
# Category validation
POSHMARK_CATEGORIES = [
    'Women', 'Men', 'Kids', 'Home', 'Beauty', 'Pets'
]

def validate_poshmark_listing(data):
    # Category check
    if data['category'] not in POSHMARK_CATEGORIES:
        raise ValueError("Category not supported on Poshmark")

    # Image requirements
    if len(data['images']) < 1 or len(data['images']) > 16:
        raise ValueError("Poshmark requires 1-16 images")

    # Authenticity check
    luxury_brands = ['Louis Vuitton', 'Gucci', 'Chanel', 'Hermès']
    if any(brand.lower() in data['title'].lower() for brand in luxury_brands):
        data['authenticity_required'] = True
        if data['price'] > 500:
            return "WARNING: High-value luxury items may require authentication"

    # Condition validation
    valid_conditions = ['NWT', 'NWOT', 'Excellent', 'Good', 'Fair', 'Poor']
    if data.get('condition') not in valid_conditions:
        data['condition'] = 'Good'  # Default

    # Posting frequency
    posts_today = count_posts_today(user.id, 'poshmark')
    if posts_today >= 100:
        raise ValueError("Poshmark daily posting limit reached")
```

---

## 🔧 CUSTOM INTEGRATION OPTIONS

### **Option 1: Custom API Integration**

**For businesses with their own inventory systems**

#### **Setup:**
```python
# User provides API endpoint
class CustomAPIIntegration:
    def __init__(self, user_config):
        self.api_url = user_config['api_endpoint']
        self.api_key = user_config['api_key']
        self.api_secret = user_config['api_secret']

    async def fetch_inventory(self):
        """Fetch inventory from customer's API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'X-API-Secret': self.api_secret
        }
        response = await httpx.get(f'{self.api_url}/inventory', headers=headers)
        return response.json()

    async def sync_listing(self, listing_id, platforms):
        """Sync single listing to multiple platforms"""
        item = await self.fetch_item(listing_id)
        results = {}

        for platform in platforms:
            try:
                result = await platform_manager.post(platform, item)
                results[platform] = {'success': True, 'id': result['id']}
            except Exception as e:
                results[platform] = {'success': False, 'error': str(e)}

        return results
```

#### **Required API Format (from customer):**
```json
{
  "inventory": [
    {
      "id": "SKU-12345",
      "title": "Product Title",
      "description": "Product description",
      "price": 99.99,
      "images": ["url1.jpg", "url2.jpg"],
      "category": "Electronics",
      "quantity": 5,
      "condition": "New",
      "location": "Phoenix, AZ"
    }
  ]
}
```

#### **Features:**
- ✅ Automatic inventory sync
- ✅ Bulk operations
- ✅ Real-time updates
- ✅ Webhook notifications
- ✅ Bi-directional sync

---

### **Option 2: Manual Mode with AI Generation**

**For users who prefer manual control**

#### **Features:**
```python
class ManualListingMode:
    """Manual listing creation with AI assistance"""

    def create_listing_wizard(self, user_input):
        """Step-by-step wizard with AI help"""

        # Step 1: Basic info
        basic_info = self.collect_basic_info(user_input)

        # Step 2: AI-enhanced description
        ai_description = self.generate_description(basic_info)
        user_can_edit = True

        # Step 3: AI-suggested pricing
        suggested_price = self.suggest_price(basic_info)
        price_range = self.get_market_range(basic_info)

        # Step 4: Platform recommendations
        recommended_platforms = self.recommend_platforms(basic_info)

        # Step 5: SEO optimization
        optimized_title = self.optimize_title(basic_info['title'])
        tags = self.generate_tags(basic_info)

        return {
            'title': optimized_title,
            'description': ai_description,
            'price': suggested_price,
            'price_range': price_range,
            'platforms': recommended_platforms,
            'tags': tags
        }

    async def generate_description(self, basic_info):
        """AI-powered description generation"""
        prompt = f"""
        Create a compelling marketplace listing description for:

        Item: {basic_info['title']}
        Category: {basic_info['category']}
        Condition: {basic_info['condition']}
        Key Features: {basic_info.get('features', 'N/A')}

        Make it:
        - Clear and honest
        - SEO-optimized
        - Platform-compliant
        - Engaging for buyers
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
```

#### **UI Flow:**
1. User uploads photo(s)
2. AI recognizes item type
3. User confirms/edits
4. AI generates description
5. AI suggests price based on market data
6. AI recommends best platforms
7. User reviews and approves
8. One-click post to selected platforms

---

### **Option 3: CSV Bulk Upload** (Team/Agency Plans)

**For high-volume sellers**

#### **CSV Format:**
```csv
title,description,price,category,condition,location,image1,image2,image3,platforms,quantity
"iPhone 13 Pro","Excellent condition...",650,"Electronics","Used","Phoenix, AZ","img1.jpg","img2.jpg","img3.jpg","ebay,facebook,offerup",1
"Nike Shoes Size 10","Brand new in box...",85,"Apparel","New","Phoenix, AZ","img4.jpg","img5.jpg","","facebook,poshmark",3
```

#### **Features:**
```python
class CSVBulkUpload:
    """Bulk upload via CSV for Team/Agency plans"""

    MAX_ROWS = {
        'team': 500,
        'agency': 5000
    }

    async def process_csv(self, file, user):
        """Process CSV upload"""

        # Check plan limits
        if user.plan not in ['team', 'agency']:
            raise ValueError("CSV upload requires Team or Agency plan")

        df = pd.read_csv(file)

        if len(df) > self.MAX_ROWS[user.plan]:
            raise ValueError(f"Exceeds limit of {self.MAX_ROWS[user.plan]} rows")

        results = []
        for idx, row in df.iterrows():
            try:
                # Validate row
                validated = self.validate_csv_row(row)

                # Create listing
                listing = await self.create_listing(validated, user)

                # Post to platforms
                platforms = row['platforms'].split(',')
                posting_results = await self.post_to_platforms(listing, platforms)

                results.append({
                    'row': idx + 1,
                    'success': True,
                    'listing_id': listing.id,
                    'results': posting_results
                })

            except Exception as e:
                results.append({
                    'row': idx + 1,
                    'success': False,
                    'error': str(e)
                })

        return results

    def validate_csv_row(self, row):
        """Validate single CSV row"""
        required_fields = ['title', 'price', 'category']

        for field in required_fields:
            if pd.isna(row.get(field)):
                raise ValueError(f"Missing required field: {field}")

        return row
```

---

## 🛡️ GLOBAL SAFEGUARDS SYSTEM

### **1. Content Filter**

```python
class ContentFilter:
    """Universal content filtering across all platforms"""

    PROHIBITED_KEYWORDS = [
        # Illegal items
        'drugs', 'marijuana', 'cocaine', 'heroin',
        'weapons', 'gun', 'firearm', 'ammunition',
        'explosives', 'bomb',

        # Counterfeit
        'replica', 'fake', 'counterfeit', 'knockoff',
        'inspired by', 'AAA quality',

        # Adult content
        'adult', 'xxx', 'porn', 'escort',

        # Scams
        'mlm', 'pyramid scheme', 'work from home',
        'get rich quick', 'guaranteed income',

        # Prohibited items
        'endangered species', 'ivory', 'live animals',
        'human remains', 'body parts',
        'prescription drugs', 'medical devices',
        'tobacco', 'vape', 'alcohol'
    ]

    def check_content(self, title, description):
        """Check for prohibited content"""
        content = f"{title} {description}".lower()

        for keyword in self.PROHIBITED_KEYWORDS:
            if keyword in content:
                return {
                    'allowed': False,
                    'reason': f'Prohibited keyword detected: {keyword}',
                    'suggestion': 'Please review marketplace policies'
                }

        return {'allowed': True}
```

### **2. Rate Limiter**

```python
class RateLimiter:
    """Platform-specific rate limiting"""

    LIMITS = {
        'ebay': {'calls': 5000, 'period': 86400},
        'facebook': {'calls': 200, 'period': 3600},
        'craigslist': {'posts': 48, 'period': 86400},
        'offerup': {'posts': 50, 'period': 86400},
        'nextdoor': {'posts': 20, 'period': 604800},
        'etsy': {'calls': 10000, 'period': 86400},
        'poshmark': {'posts': 100, 'period': 86400}
    }

    async def check_limit(self, user_id, platform, action='post'):
        """Check if action is within rate limits"""
        key = f"{user_id}:{platform}:{action}"

        count = await redis.get(key) or 0
        limit = self.LIMITS[platform]

        if count >= limit['calls'] or count >= limit.get('posts', float('inf')):
            next_reset = await redis.ttl(key)
            raise RateLimitError(
                f"Rate limit exceeded for {platform}. "
                f"Resets in {next_reset} seconds."
            )

        # Increment counter
        await redis.incr(key)
        await redis.expire(key, limit['period'])

        return True
```

### **3. Duplicate Detector**

```python
class DuplicateDetector:
    """Prevent duplicate listings"""

    async def check_duplicate(self, user_id, platform, listing_data):
        """Check for duplicate listings"""

        # Check same platform
        existing = await db.listings.find_one({
            'user_id': user_id,
            'platform': platform,
            'title': {'$regex': f'^{listing_data["title"]}$', '$options': 'i'},
            'status': {'$in': ['active', 'pending']},
            'created_at': {'$gte': datetime.now() - timedelta(days=30)}
        })

        if existing:
            return {
                'is_duplicate': True,
                'existing_id': existing['_id'],
                'message': f'Similar listing exists on {platform}'
            }

        # Check across platforms (for Craigslist multi-city protection)
        if platform == 'craigslist':
            recent_posts = await db.listings.count_documents({
                'user_id': user_id,
                'platform': 'craigslist',
                'title': {'$regex': f'^{listing_data["title"]}$', '$options': 'i'},
                'created_at': {'$gte': datetime.now() - timedelta(hours=48)}
            })

            if recent_posts >= 3:  # Max 3 cities per 48 hours
                return {
                    'is_duplicate': True,
                    'message': 'Craigslist: Wait 48 hours before posting to more cities'
                }

        return {'is_duplicate': False}
```

### **4. Image Validator**

```python
class ImageValidator:
    """Validate images meet platform requirements"""

    REQUIREMENTS = {
        'ebay': {'min': 1, 'max': 24, 'min_size': 500, 'formats': ['jpg', 'jpeg', 'png']},
        'facebook': {'min': 1, 'max': 10, 'min_size': 200, 'formats': ['jpg', 'jpeg', 'png']},
        'craigslist': {'min': 1, 'max': 24, 'min_size': 300, 'formats': ['jpg', 'jpeg', 'png', 'gif']},
        'offerup': {'min': 1, 'max': 12, 'min_size': 300, 'formats': ['jpg', 'jpeg', 'png']},
        'nextdoor': {'min': 1, 'max': 10, 'min_size': 400, 'formats': ['jpg', 'jpeg', 'png']},
        'etsy': {'min': 1, 'max': 10, 'min_size': 1000, 'formats': ['jpg', 'jpeg', 'png', 'gif']},
        'poshmark': {'min': 1, 'max': 16, 'min_size': 400, 'formats': ['jpg', 'jpeg', 'png']}
    }

    async def validate_images(self, images, platform):
        """Validate images for specific platform"""
        req = self.REQUIREMENTS[platform]

        # Count check
        if len(images) < req['min']:
            raise ValueError(f"{platform} requires at least {req['min']} image(s)")
        if len(images) > req['max']:
            raise ValueError(f"{platform} allows maximum {req['max']} images")

        # Validate each image
        for idx, img_url in enumerate(images):
            # Download and check
            img_data = await self.download_image(img_url)
            img = Image.open(io.BytesIO(img_data))

            # Size check
            if min(img.size) < req['min_size']:
                raise ValueError(
                    f"Image {idx+1} too small. "
                    f"{platform} requires {req['min_size']}x{req['min_size']}px minimum"
                )

            # Format check
            img_format = img.format.lower()
            if img_format not in req['formats']:
                raise ValueError(
                    f"Image {idx+1} format not supported. "
                    f"{platform} accepts: {', '.join(req['formats'])}"
                )

        return True
```

### **5. Price Validator**

```python
class PriceValidator:
    """Validate pricing meets platform requirements"""

    LIMITS = {
        'ebay': {'min': 0.01, 'max': 100000000},
        'facebook': {'min': 0.01, 'max': 500000},
        'craigslist': {'min': 0, 'max': None},
        'offerup': {'min': 1, 'max': 50000},
        'nextdoor': {'min': 0, 'max': 50000},
        'etsy': {'min': 0.20, 'max': 100000},
        'poshmark': {'min': 3, 'max': 10000}
    }

    def validate_price(self, price, platform):
        """Validate price for platform"""
        limits = self.LIMITS[platform]

        if price < limits['min']:
            raise ValueError(
                f"{platform} minimum price: ${limits['min']}"
            )

        if limits['max'] and price > limits['max']:
            raise ValueError(
                f"{platform} maximum price: ${limits['max']}"
            )

        return True
```

---

## 📋 IMPLEMENTATION CHECKLIST

### **Phase 1: Foundation (Week 1-2)**
- [ ] Set up platform credentials management system
- [ ] Implement global safeguards (content filter, rate limiter)
- [ ] Create unified listing model
- [ ] Build platform abstraction layer

### **Phase 2: New Platform Integration (Week 3-6)**
- [ ] Nextdoor integration (API or automation)
- [ ] Etsy OAuth integration
- [ ] Poshmark automation
- [ ] Testing for each platform

### **Phase 3: Advanced Features (Week 7-8)**
- [ ] Custom API integration system
- [ ] Manual mode with AI wizard
- [ ] CSV bulk upload
- [ ] Webhook system

### **Phase 4: Testing & Launch (Week 9-10)**
- [ ] End-to-end testing all platforms
- [ ] Compliance review
- [ ] Beta user testing
- [ ] Production launch

---

## 🚀 NEXT STEPS

1. **Apply for API access:**
   - Nextdoor Business API
   - Etsy Developer Account
   - Verify all existing API apps

2. **Set up monitoring:**
   - Rate limit tracking
   - Error logging
   - Compliance alerts

3. **Create documentation:**
   - Platform-specific guides
   - API integration docs
   - CSV upload templates

4. **Build admin dashboard:**
   - Monitor all platform connections
   - View rate limit status
   - Handle compliance issues

---

**Ready to expand to 7+ platforms with bulletproof safeguards!** 🚀🛡️
