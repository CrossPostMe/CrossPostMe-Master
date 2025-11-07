import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Checkbox } from "../components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Plus,
  Sparkles,
  Loader2,
  AlertCircle,
  CheckCircle2
} from "lucide-react";
import { api } from "../lib/api";

const CreateAd = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    price: "",
    category: "",
    location: "",
    images: [],
    platforms: [],
  });

  const categories = [
    "Electronics",
    "Furniture",
    "Vehicles",
    "Real Estate",
    "Appliances",
    "Clothing",
    "Sports",
    "Tools",
    "Other"
  ];

  const platforms = [
    { id: "facebook", name: "Facebook Marketplace", icon: "📘" },
    { id: "ebay", name: "eBay", icon: "🛒" },
    { id: "offerup", name: "OfferUp", icon: "📱" },
    { id: "craigslist", name: "Craigslist", icon: "📝" },
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePlatformToggle = (platformId) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };

  const handleImageAdd = (e) => {
    const url = prompt("Enter image URL:");
    if (url) {
      setFormData(prev => ({
        ...prev,
        images: [...prev.images, url]
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    // Validation
    if (!formData.title || !formData.description || !formData.price) {
      setError("Please fill in all required fields");
      return;
    }

    if (formData.platforms.length === 0) {
      setError("Please select at least one platform");
      return;
    }

    try {
      setLoading(true);

      const adData = {
        ...formData,
        price: parseFloat(formData.price),
        status: "draft"
      };

      const response = await api.post("/api/ads/", adData);

      setSuccess(true);
      setTimeout(() => {
        navigate("/marketplace/my-ads");
      }, 1500);

    } catch (err) {
      console.error("Error creating ad:", err);
      setError(err.message || "Failed to create ad. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAIGenerate = async () => {
    if (!formData.title) {
      alert("Please enter a title first");
      return;
    }

    try {
      setLoading(true);
      const response = await api.post("/api/listing-assistant/generate", {
        keywords: formData.title.split(" "),
        category: formData.category || "General",
        platforms: formData.platforms.length > 0 ? formData.platforms : ["facebook"]
      });

      if (response.content) {
        setFormData(prev => ({
          ...prev,
          description: response.content
        }));
      }
    } catch (err) {
      console.error("AI generation failed:", err);
      alert("AI generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Create New Ad</h2>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {success && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-5 w-5" />
              <span className="font-medium">Ad created successfully! Redirecting...</span>
            </div>
          </CardContent>
        </Card>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Ad Details</CardTitle>
            <CardDescription>
              Provide information about your item
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">
                Title <span className="text-red-500">*</span>
              </Label>
              <Input
                id="title"
                name="title"
                placeholder="e.g., iPhone 13 Pro Max - Unlocked"
                value={formData.title}
                onChange={handleInputChange}
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="description">
                  Description <span className="text-red-500">*</span>
                </Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAIGenerate}
                  disabled={loading || !formData.title}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  AI Generate
                </Button>
              </div>
              <Textarea
                id="description"
                name="description"
                placeholder="Describe your item in detail..."
                rows={6}
                value={formData.description}
                onChange={handleInputChange}
                required
              />
              <p className="text-sm text-gray-500">
                Tip: Include condition, features, and why someone should buy it
              </p>
            </div>

            {/* Price */}
            <div className="space-y-2">
              <Label htmlFor="price">
                Price <span className="text-red-500">*</span>
              </Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                  $
                </span>
                <Input
                  id="price"
                  name="price"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  className="pl-7"
                  value={formData.price}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) =>
                  setFormData(prev => ({ ...prev, category: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                name="location"
                placeholder="e.g., Phoenix, AZ"
                value={formData.location}
                onChange={handleInputChange}
              />
            </div>

            {/* Images */}
            <div className="space-y-2">
              <Label>Images</Label>
              <div className="space-y-2">
                {formData.images.map((url, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input value={url} readOnly />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setFormData(prev => ({
                          ...prev,
                          images: prev.images.filter((_, i) => i !== index)
                        }));
                      }}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleImageAdd}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Image URL
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Platforms */}
        <Card>
          <CardHeader>
            <CardTitle>Select Platforms</CardTitle>
            <CardDescription>
              Choose where you want to post this ad
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {platforms.map((platform) => (
                <div
                  key={platform.id}
                  className={`flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                    formData.platforms.includes(platform.id)
                      ? "border-blue-500 bg-blue-50"
                      : ""
                  }`}
                  onClick={() => handlePlatformToggle(platform.id)}
                >
                  <Checkbox
                    checked={formData.platforms.includes(platform.id)}
                    onCheckedChange={() => handlePlatformToggle(platform.id)}
                  />
                  <span className="text-2xl">{platform.icon}</span>
                  <span className="font-medium">{platform.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Submit */}
        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/dashboard")}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Create Ad
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CreateAd;
