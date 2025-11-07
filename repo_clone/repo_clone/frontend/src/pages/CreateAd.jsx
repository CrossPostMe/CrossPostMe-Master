import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { toast } from '../hooks/use-toast';
import { ArrowLeft, Sparkles } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CreateAd = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    category: '',
    location: '',
    platforms: [],
    auto_renew: false
  });

  const platforms = [
    { id: 'facebook', name: 'Facebook Marketplace' },
    { id: 'craigslist', name: 'Craigslist' },
    { id: 'offerup', name: 'OfferUp' },
    { id: 'nextdoor', name: 'Nextdoor' }
  ];

  const categories = [
    'Electronics', 'Furniture', 'Vehicles', 'Real Estate',
    'Appliances', 'Clothing', 'Sports', 'Tools', 'Other'
  ];

  const handlePlatformToggle = (platformId) => {
    setFormData(prev => {
      const platforms = prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId];
      return { ...prev, platforms };
    });
  };

  const generateWithAI = async () => {
    if (!formData.title || !formData.price || !formData.category) {
      toast({
        title: 'Missing Information',
        description: 'Please fill in product name, price, and category first.',
        variant: 'destructive'
      });
      return;
    }

    setAiLoading(true);
    try {
      const response = await axios.post(`${API}/ai/generate-ad`, {
        product_name: formData.title,
        product_details: formData.description || 'Great condition item',
        price: parseFloat(formData.price),
        category: formData.category,
        tone: 'professional'
      });

      setFormData(prev => ({
        ...prev,
        title: response.data.title,
        description: response.data.description
      }));

      toast({
        title: 'AI Generation Complete!',
        description: 'Your ad has been optimized with AI.'
      });
    } catch (error) {
      console.error('Error generating ad:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate ad with AI.',
        variant: 'destructive'
      });
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.platforms.length === 0) {
      toast({
        title: 'Select Platforms',
        description: 'Please select at least one platform to post to.',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      const adData = {
        ...formData,
        price: parseFloat(formData.price),
        images: []
      };

      const response = await axios.post(`${API}/ads/`, adData);
      
      // Post to selected platforms
      for (const platform of formData.platforms) {
        await axios.post(`${API}/ads/${response.data.id}/post?platform=${platform}`);
      }

      toast({
        title: 'Ad Created Successfully!',
        description: `Your ad has been posted to ${formData.platforms.length} platform(s).`
      });

      navigate('/marketplace/my-ads');
    } catch (error) {
      console.error('Error creating ad:', error);
      toast({
        title: 'Error',
        description: 'Failed to create ad. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/marketplace/dashboard')}
          className="mb-6"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create New Ad</h1>
          <p className="text-gray-600 mt-1">Fill in the details below to create your marketplace listing</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Card className="p-6 mb-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">Ad Details</h2>
              <Button
                type="button"
                onClick={generateWithAI}
                disabled={aiLoading}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {aiLoading ? 'Generating...' : 'Generate with AI'}
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name / Title *
                </label>
                <Input
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., 2015 Honda Civic"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price *
                  </label>
                  <Input
                    required
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => setFormData({ ...formData, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
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
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location *
                </label>
                <Input
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="City, State"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <Textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe your item in detail..."
                  rows={6}
                />
              </div>
            </div>
          </Card>

          <Card className="p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Select Platforms</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {platforms.map((platform) => (
                <div
                  key={platform.id}
                  className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => handlePlatformToggle(platform.id)}
                >
                  <Checkbox
                    checked={formData.platforms.includes(platform.id)}
                    onCheckedChange={() => handlePlatformToggle(platform.id)}
                  />
                  <label className="font-medium cursor-pointer">{platform.name}</label>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6 mb-6">
            <div className="flex items-center space-x-3">
              <Checkbox
                checked={formData.auto_renew}
                onCheckedChange={(checked) => setFormData({ ...formData, auto_renew: checked })}
              />
              <div>
                <label className="font-medium">Auto-Renew</label>
                <p className="text-sm text-gray-600">
                  Automatically repost this ad when it expires
                </p>
              </div>
            </div>
          </Card>

          <div className="flex space-x-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
            >
              {loading ? 'Creating...' : 'Create & Post Ad'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/marketplace/dashboard')}
              className="px-8 py-6"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAd;