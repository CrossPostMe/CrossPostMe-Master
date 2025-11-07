import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { TrendingUp, Eye, MessageSquare, BarChart3, Plus } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/ads/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Ads',
      value: stats?.total_ads || 0,
      icon: BarChart3,
      color: 'blue',
      change: '+12%'
    },
    {
      title: 'Active Posts',
      value: stats?.active_ads || 0,
      icon: TrendingUp,
      color: 'green',
      change: '+8%'
    },
    {
      title: 'Total Views',
      value: stats?.total_views || 0,
      icon: Eye,
      color: 'purple',
      change: '+23%'
    },
    {
      title: 'Total Leads',
      value: stats?.total_leads || 0,
      icon: MessageSquare,
      color: 'orange',
      change: '+15%'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome back! Here's your marketplace overview.</p>
          </div>
          <Link to="/marketplace/create-ad">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="w-5 h-5 mr-2" />
              Create New Ad
            </Button>
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                  </div>
                  <span className="text-sm font-semibold text-green-600">{stat.change}</span>
                </div>
                <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </Card>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6">
          <Link to="/marketplace/my-ads">
            <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
              <h3 className="text-lg font-bold text-gray-900 mb-2">My Ads</h3>
              <p className="text-gray-600 mb-4">View and manage all your advertisements</p>
              <Button variant="outline" className="w-full">View Ads</Button>
            </Card>
          </Link>

          <Link to="/marketplace/platforms">
            <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Platforms</h3>
              <p className="text-gray-600 mb-4">Manage connected marketplace accounts</p>
              <Button variant="outline" className="w-full">Manage Platforms</Button>
            </Card>
          </Link>

          <Link to="/marketplace/analytics">
            <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Analytics</h3>
              <p className="text-gray-600 mb-4">Track performance and insights</p>
              <Button variant="outline" className="w-full">View Analytics</Button>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;