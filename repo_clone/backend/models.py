import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


# Platform Account Models
class PlatformAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # User identifier for multi-tenant support
    platform: str  # facebook, craigslist, offerup, nextdoor
    account_name: str
    account_email: str
    status: str = "active"  # active, suspended, flagged
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None


class PlatformAccountCreate(BaseModel):
    platform: str
    account_name: str
    account_email: str


# Ad Models
class Ad(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # User identifier for multi-tenant support
    title: str
    description: str
    price: float
    category: str
    location: str
    images: List[str] = []
    platforms: List[str] = []  # Which platforms to post to
    status: str = "draft"  # draft, scheduled, posted, paused
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_time: Optional[datetime] = None
    auto_renew: bool = False


class AdCreate(BaseModel):
    user_id: str = "default"  # User identifier for multi-tenant support
    title: str
    description: str
    price: float
    category: str
    location: str
    images: List[str] = []
    platforms: List[str] = []
    scheduled_time: Optional[datetime] = None
    auto_renew: bool = False


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    auto_renew: Optional[bool] = None


# Posted Ad Models
class PostedAd(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ad_id: str
    platform: str
    platform_ad_id: Optional[str] = None
    post_url: Optional[str] = None
    posted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"  # active, expired, removed, flagged
    views: int = 0
    clicks: int = 0
    leads: int = 0


class PostedAdCreate(BaseModel):
    ad_id: str
    platform: str
    platform_ad_id: Optional[str] = None
    post_url: Optional[str] = None


# Analytics Models
class AdAnalytics(BaseModel):
    ad_id: str
    platform: str
    views: int = 0
    clicks: int = 0
    leads: int = 0
    messages: int = 0
    conversion_rate: float = 0.0
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DashboardStats(BaseModel):
    total_ads: int
    active_ads: int
    total_posts: int
    total_views: int
    total_leads: int
    platforms_connected: int


# AI Generation Models
class AIAdRequest(BaseModel):
    product_name: str
    product_details: str
    price: float
    category: str
    tone: str = "professional"  # professional, casual, urgent


class AIAdResponse(BaseModel):
    title: str
    description: str
    suggested_categories: List[str]
    keywords: List[str]


# Incoming Message Models
class IncomingMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # User identifier for multi-tenant support
    ad_id: Optional[str] = None  # Which ad this message relates to
    platform: str  # facebook, craigslist, offerup, nextdoor
    platform_message_id: Optional[str] = None  # Platform's internal message ID
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    sender_phone: Optional[str] = None
    sender_profile_url: Optional[str] = None
    subject: Optional[str] = None
    message_text: str
    message_type: str = "inquiry"  # inquiry, offer, question, complaint
    source_type: str = "platform"  # platform, email, parsed_notification
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_read: bool = False
    is_responded: bool = False
    priority: str = "normal"  # low, normal, high, urgent
    raw_data: Optional[dict] = None  # Store original platform data


class IncomingMessageCreate(BaseModel):
    ad_id: Optional[str] = None
    platform: str
    platform_message_id: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    sender_phone: Optional[str] = None
    sender_profile_url: Optional[str] = None
    subject: Optional[str] = None
    message_text: str
    message_type: str = "inquiry"
    source_type: str = "platform"
    priority: str = "normal"
    raw_data: Optional[dict] = None


# Lead Management Models
class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    ad_id: Optional[str] = None
    platform: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    interest_level: str = "unknown"  # unknown, low, medium, high, very_high
    status: str = "new"  # new, contacted, qualified, negotiating, sold, lost
    source_message_id: Optional[str] = None  # First message that created this lead
    last_contact_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    tags: List[str] = []


class LeadCreate(BaseModel):
    ad_id: Optional[str] = None
    platform: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    interest_level: str = "unknown"
    source_message_id: Optional[str] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    tags: List[str] = []


class LeadUpdate(BaseModel):
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    interest_level: Optional[str] = None
    status: Optional[str] = None
    last_contact_at: Optional[datetime] = None
    notes: Optional[str] = None
    estimated_value: Optional[float] = None
    tags: Optional[List[str]] = None


# Response Templates
class ResponseTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    name: str
    subject: Optional[str] = None
    template_text: str
    template_type: str = (
        "general"  # general, price_inquiry, availability, meeting_request
    )
    platforms: List[str] = []  # Which platforms this template is suitable for
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResponseTemplateCreate(BaseModel):
    name: str
    subject: Optional[str] = None
    template_text: str
    template_type: str = "general"
    platforms: List[str] = []


# Outgoing Response Models
class OutgoingResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    message_id: str  # Which incoming message this responds to
    lead_id: Optional[str] = None
    platform: str
    response_text: str
    response_method: str = "platform"  # platform, email, sms
    sent_at: Optional[datetime] = None
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    template_used: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OutgoingResponseCreate(BaseModel):
    message_id: str
    lead_id: Optional[str] = None
    platform: str
    response_text: str
    response_method: str = "platform"
    template_used: Optional[str] = None


# Email Monitoring Models
class EmailRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    platform: str
    sender_pattern: str  # Email pattern to match (e.g., "*@craigslist.org")
    subject_patterns: List[str] = (
        []
    )  # Subject line patterns to identify platform notifications
    parsing_rules: dict = {}  # Rules for extracting data from email content
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmailRuleCreate(BaseModel):
    platform: str
    sender_pattern: str
    subject_patterns: List[str] = []
    parsing_rules: dict = {}


# Platform Monitoring Config
class PlatformMonitoringConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    platform: str
    monitoring_enabled: bool = True
    check_interval_minutes: int = 15  # How often to check for new messages
    email_monitoring: bool = True
    platform_scraping: bool = True  # Direct platform message scraping
    last_check_at: Optional[datetime] = None
    credentials_id: Optional[str] = None  # Reference to stored credentials
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformMonitoringConfigCreate(BaseModel):
    platform: str
    monitoring_enabled: bool = True
    check_interval_minutes: int = 15
    email_monitoring: bool = True
    platform_scraping: bool = True
    credentials_id: Optional[str] = None
