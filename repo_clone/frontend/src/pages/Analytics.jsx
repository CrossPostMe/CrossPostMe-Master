import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, TrendingUp, Eye, MessageSquare, BarChart3, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Analytics = () => {
  const [ads, setAds] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('7');

  useEffect(() => {
    fetchAnalytics();
  }, [selectedPeriod]);

  const fetchAnalytics = async () => {
    try {
      // Fetch ads
      const adsResponse = await axios.get(`${API}/ads/`);
      setAds(adsResponse.data);

      // Fetch analytics for each ad
      const analyticsData = {};
      for (const ad of adsResponse.data) {
        try {
          const analyticsResponse = await axios.get(`${API}/ads/${ad.id}/analytics?days=${selectedPeriod}`);
          analyticsData[ad.id] = analyticsResponse.data;
        } catch (error) {
          console.error(`Error fetching analytics for ad ${ad.id}:`, error);
        }
      }
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTotalMetrics = () => {
    let totalViews = 0;
    let totalClicks = 0;
    let totalLeads = 0;
    let totalMessages = 0;

    Object.values(analytics).forEach(adAnalytics => {
      adAnalytics.forEach(platform => {
        totalViews += platform.views;
        totalClicks += platform.clicks;
        totalLeads += platform.leads;
        totalMessages += platform.messages;
      });
    });

    return { totalViews, totalClicks, totalLeads, totalMessages };
  };

  const metrics = getTotalMetrics();

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
              <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
              <p className="text-gray-600 mt-1">Performance insights for your ads</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="px-3 py-2 border rounded-lg"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Eye className="w-6 h-6 text-blue-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-green-600" />
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">Total Views</h3>
            <p className="text-3xl font-bold text-gray-900">{metrics.totalViews.toLocaleString()}</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-green-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-green-600" />
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">Total Clicks</h3>
            <p className="text-3xl font-bold text-gray-900">{metrics.totalClicks.toLocaleString()}</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-purple-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-green-600" />
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">Total Leads</h3>
            <p className="text-3xl font-bold text-gray-900">{metrics.totalLeads.toLocaleString()}</p>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-orange-600" />
              </div>
              <TrendingUp className="w-4 h-4 text-green-600" />
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-1">Messages</h3>
            <p className="text-3xl font-bold text-gray-900">{metrics.totalMessages.toLocaleString()}</p>
          </Card>
        </div>

        {/* Ad Performance */}
        <Card className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Ad Performance</h2>
          
          {ads.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">No ads to analyze</p>
              <Link to="/marketplace/create-ad">
                <Button>Create Your First Ad</Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-6">
              {ads.map((ad) => {
                const adAnalytics = analytics[ad.id] || [];
                const totalViews = adAnalytics.reduce((sum, platform) => sum + platform.views, 0);
                const totalClicks = adAnalytics.reduce((sum, platform) => sum + platform.clicks, 0);
                const totalLeads = adAnalytics.reduce((sum, platform) => sum + platform.leads, 0);
                const avgConversion = adAnalytics.length > 0 
                  ? adAnalytics.reduce((sum, platform) => sum + platform.conversion_rate, 0) / adAnalytics.length 
                  : 0;

                return (
                  <div key={ad.id} className="border rounded-lg p-6 bg-white">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-lg text-gray-900">{ad.title}</h3>
                        <p className="text-gray-600 text-sm">{ad.category} • ${ad.price}</p>
                      </div>
                      <Badge variant={ad.status === 'posted' ? 'default' : 'secondary'}>
                        {ad.status.charAt(0).toUpperCase() + ad.status.slice(1)}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-blue-600">{totalViews.toLocaleString()}</p>
                        <p className="text-sm text-gray-600">Views</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-600">{totalClicks.toLocaleString()}</p>
                        <p className="text-sm text-gray-600">Clicks</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-purple-600">{totalLeads.toLocaleString()}</p>
                        <p className="text-sm text-gray-600">Leads</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-orange-600">{avgConversion.toFixed(1)}%</p>
                        <p className="text-sm text-gray-600">Conversion</p>
                      </div>
                    </div>

                    {/* Platform Breakdown */}
                    {adAnalytics.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Platform Performance</h4>
                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3">
                          {adAnalytics.map((platform, index) => (
                            <div key={platform.platform || `platform-${index}`} className="bg-gray-50 rounded-lg p-3">
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-medium text-sm capitalize">{platform.platform}</span>
                                <span className="text-xs text-gray-500">{platform.conversion_rate}%</span>
                              </div>
                              <div className="text-xs text-gray-600 space-y-1">
                                <div className="flex justify-between">
                                  <span>Views:</span>
                                  <span>{platform.views}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Leads:</span>
                                  <span>{platform.leads}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Analytics;