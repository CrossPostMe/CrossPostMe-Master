import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, Eye, MessageSquare, Edit, Trash2, Plus } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MyAds = () => {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAds();
  }, [filter]);

  const fetchAds = async () => {
    try {
      const url = filter === 'all' ? `${API}/ads/` : `${API}/ads/?status=${filter}`;
      const response = await axios.get(url);
      setAds(response.data);
    } catch (error) {
      console.error('Error fetching ads:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteAd = async (adId) => {
    if (!window.confirm('Are you sure you want to delete this ad?')) return;

    try {
      await axios.delete(`${API}/ads/${adId}`);
      toast({
        title: 'Ad Deleted',
        description: 'The ad has been successfully removed.'
      });
      fetchAds();
    } catch (error) {
      console.error('Error deleting ad:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete ad.',
        variant: 'destructive'
      });
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      draft: 'secondary',
      posted: 'default',
      paused: 'destructive'
    };
    return (
      <Badge variant={variants[status] || 'secondary'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-4">
            <Link to="/marketplace/dashboard">
              <Button variant="ghost">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Ads</h1>
              <p className="text-gray-600 mt-1">{ads.length} total advertisements</p>
            </div>
          </div>
          <Link to="/marketplace/create-ad">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="w-5 h-5 mr-2" />
              Create New Ad
            </Button>
          </Link>
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-2 mb-6">
          {['all', 'draft', 'posted', 'paused'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              onClick={() => setFilter(status)}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Button>
          ))}
        </div>

        {/* Ads Grid */}
        {ads.length === 0 ? (
          <Card className="p-12 text-center">
            <p className="text-gray-600 mb-4">No ads found</p>
            <Link to="/marketplace/create-ad">
              <Button>Create Your First Ad</Button>
            </Link>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ads.map((ad) => (
              <Card key={ad.id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-gray-900 mb-2 line-clamp-2">
                      {ad.title}
                    </h3>
                    {getStatusBadge(ad.status)}
                  </div>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{ad.description}</p>

                <div className="flex items-center justify-between mb-4">
                  <span className="text-2xl font-bold text-blue-600">${ad.price}</span>
                  <span className="text-sm text-gray-500">{ad.category}</span>
                </div>

                <div className="flex items-center space-x-4 mb-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <Eye className="w-4 h-4" />
                    <span>245</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MessageSquare className="w-4 h-4" />
                    <span>12</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  {ad.platforms.map((platform) => (
                    <Badge key={platform} variant="outline" className="text-xs">
                      {platform}
                    </Badge>
                  ))}
                </div>

                <div className="flex space-x-2">
                  <Link to={`/marketplace/edit-ad/${ad.id}`} className="flex-1">
                    <Button variant="outline" className="w-full" size="sm">
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => deleteAd(ad.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyAds;