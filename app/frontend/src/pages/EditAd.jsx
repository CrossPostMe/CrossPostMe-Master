import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { toast } from '../hooks/use-toast';
import { ArrowLeft, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EditAd = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    category: '',
    location: '',
    platforms: [],
    auto_renew: false,
    status: 'draft'
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

  const statuses = [
    { value: 'draft', label: 'Draft' },
    { value: 'posted', label: 'Posted' },
    { value: 'paused', label: 'Paused' }
  ];

  useEffect(() => {
    fetchAd();
  }, [id]);

  const fetchAd = async () => {
    try {
      const response = await axios.get(`${API}/ads/${id}`);
      const ad = response.data;
      setFormData({
        title: ad.title,
        description: ad.description,
        price: ad.price.toString(),
        category: ad.category,
        location: ad.location,
        platforms: ad.platforms || [],
        auto_renew: ad.auto_renew || false,
        status: ad.status
      });
    } catch (error) {
      console.error('Error fetching ad:', error);
      toast({
        title: 'Error',
        description: 'Failed to load ad details.',
        variant: 'destructive'
      });
      navigate('/marketplace/my-ads');
    } finally {
      setInitialLoading(false);
    }
  };

  const handlePlatformToggle = (platformId) => {
    setFormData(prev => {
      const platforms = prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId];
      return { ...prev, platforms };
    });
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
      const updateData = {
        title: formData.title,
        description: formData.description,
        price: parseFloat(formData.price),
        category: formData.category,
        location: formData.location,
        platforms: formData.platforms,
        auto_renew: formData.auto_renew,
        status: formData.status
      };

      await axios.put(`${API}/ads/${id}`, updateData);

      toast({
        title: 'Ad Updated Successfully!',
        description: 'Your ad has been updated.'
      });

      navigate('/marketplace/my-ads');
    } catch (error) {
      console.error('Error updating ad:', error);
      toast({
        title: 'Error',
        description: 'Failed to update ad. Please try again.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/marketplace/my-ads')}
          className="mb-6"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to My Ads
        </Button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Edit Ad</h1>
          <p className="text-gray-600 mt-1">Update your marketplace listing details</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Card className="p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Ad Details</h2>

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

              <div className="grid md:grid-cols-3 gap-4">
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

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status *
                  </label>
                  <Select
                    value={formData.status}
                    onValueChange={(value) => setFormData({ ...formData, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      {statuses.map((status) => (
                        <SelectItem key={status.value} value={status.value}>
                          {status.label}
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
              <Save className="w-5 h-5 mr-2" />
              {loading ? 'Updating...' : 'Update Ad'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/marketplace/my-ads')}
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

export default EditAd;