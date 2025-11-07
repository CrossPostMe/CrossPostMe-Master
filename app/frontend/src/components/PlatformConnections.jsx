import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Alert, AlertDescription } from './ui/alert';
import { 
  Facebook, 
  Package, 
  ShoppingBag, 
  MapPin, 
  CheckCircle, 
  AlertCircle, 
  ExternalLink, 
  Trash2,
  Shield,
  Zap
} from 'lucide-react';
import { toast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PlatformConnections = () => {
  const [platforms, setPlatforms] = useState([]);
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState(null);
  const [credentialsDialog, setCredentialsDialog] = useState({ open: false, platform: null, data: null });
  const [credentials, setCredentials] = useState({});

  // Platform icons mapping
  const platformIcons = {
    facebook: Facebook,
    ebay: Package,
    offerup: ShoppingBag,
    craigslist: MapPin,
    whatnot: Zap,
    nextdoor: MapPin
  };

  // Platform colors
  const platformColors = {
    facebook: 'bg-blue-600 hover:bg-blue-700',
    ebay: 'bg-yellow-600 hover:bg-yellow-700',
    offerup: 'bg-green-600 hover:bg-green-700',
    craigslist: 'bg-purple-600 hover:bg-purple-700',
    whatnot: 'bg-orange-600 hover:bg-orange-700',
    nextdoor: 'bg-teal-600 hover:bg-teal-700'
  };

  useEffect(() => {
    fetchSupportedPlatforms();
    fetchConnectedPlatforms();
  }, []);

  const fetchSupportedPlatforms = async () => {
    try {
      const response = await axios.get(`${API}/platforms/supported`);
      setPlatforms(Object.entries(response.data.platforms).map(([key, value]) => ({
        id: key,
        ...value
      })));
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load supported platforms",
        variant: "destructive",
      });
    }
  };

  const fetchConnectedPlatforms = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/platforms/connected`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConnectedPlatforms(response.data);
      setLoading(false);
    } catch (error) {
      toast({
        title: "Error", 
        description: "Failed to load connected platforms",
        variant: "destructive",
      });
      setLoading(false);
    }
  };

  const handlePlatformConnect = async (platformId) => {
    setConnectingPlatform(platformId);
    
    try {
      const token = localStorage.getItem('token');
      const redirectUri = `${window.location.origin}/oauth/callback`;
      
      const response = await axios.post(`${API}/platforms/connect`, {
        platform: platformId,
        redirect_uri: redirectUri
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const result = response.data;

      if (result.method === 'oauth' && result.auth_url) {
        // Redirect to OAuth provider
        window.location.href = result.auth_url;
      } else if (result.method === 'credentials') {
        // Show credentials dialog
        setCredentialsDialog({
          open: true,
          platform: platformId,
          data: result
        });
      }

    } catch (error) {
      toast({
        title: "Connection Error",
        description: error.response?.data?.detail || "Failed to initiate platform connection",
        variant: "destructive",
      });
    } finally {
      setConnectingPlatform(null);
    }
  };

  const handleCredentialsSubmit = async () => {
    if (!credentialsDialog.platform || !credentialsDialog.data) return;

    try {
      const token = localStorage.getItem('token');
      const platform = credentialsDialog.platform;

      const response = await axios.post(`${API}/platforms/${platform}/credentials`, {
        platform: platform,
        credentials: credentials
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast({
        title: "Success",
        description: response.data.message,
      });

      setCredentialsDialog({ open: false, platform: null, data: null });
      setCredentials({});
      fetchConnectedPlatforms(); // Refresh connected platforms

    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to store credentials",
        variant: "destructive",
      });
    }
  };

  const handlePlatformDisconnect = async (platformId) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.delete(`${API}/platforms/${platformId}/disconnect`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast({
        title: "Disconnected",
        description: response.data.message,
      });

      fetchConnectedPlatforms(); // Refresh connected platforms

    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to disconnect platform",
        variant: "destructive",
      });
    }
  };

  const isPlatformConnected = (platformId) => {
    return connectedPlatforms.some(cp => cp.platform === platformId);
  };

  const getConnectedPlatformInfo = (platformId) => {
    return connectedPlatforms.find(cp => cp.platform === platformId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Connect Your Marketplace Platforms
        </h2>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Connect your marketplace accounts to enable automated posting and management. 
          We use secure OAuth when available or encrypted credential storage.
        </p>
      </div>

      {/* Platform Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        {platforms.map((platform) => {
          const Icon = platformIcons[platform.id];
          const isConnected = isPlatformConnected(platform.id);
          const connectedInfo = getConnectedPlatformInfo(platform.id);
          const isConnecting = connectingPlatform === platform.id;

          return (
            <Card key={platform.id} className="relative">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg text-white ${platformColors[platform.id]}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{platform.name}</CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        {isConnected ? (
                          <Badge variant="success" className="bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Connected
                          </Badge>
                        ) : (
                          <Badge variant="secondary">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            Not Connected
                          </Badge>
                        )}
                        <Badge variant="outline" className="text-xs">
                          {platform.oauth_available ? (
                            <><Shield className="w-3 h-3 mr-1" />OAuth</>
                          ) : (
                            <><Zap className="w-3 h-3 mr-1" />Credentials</>
                          )}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  {isConnected && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePlatformDisconnect(platform.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                <CardDescription className="mb-4">
                  {platform.description}
                </CardDescription>
                
                {/* Features */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Features:</p>
                  <div className="flex flex-wrap gap-1">
                    {platform.features.map((feature, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Connection Status */}
                {isConnected ? (
                  <div className="bg-green-50 p-3 rounded-lg">
                    <p className="text-sm text-green-800">
                      <CheckCircle className="w-4 h-4 inline mr-2" />
                      Connected on {new Date(connectedInfo.connected_at).toLocaleDateString()}
                    </p>
                    {connectedInfo.user_info?.name && (
                      <p className="text-xs text-green-700 mt-1">
                        Account: {connectedInfo.user_info.name}
                      </p>
                    )}
                  </div>
                ) : (
                  <Button
                    onClick={() => handlePlatformConnect(platform.id)}
                    disabled={isConnecting}
                    className={`w-full ${platformColors[platform.id]} text-white`}
                  >
                    {isConnecting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Connecting...
                      </>
                    ) : (
                      <>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Connect {platform.name}
                      </>
                    )}
                  </Button>
                )}

                {/* OAuth Note */}
                {platform.note && (
                  <Alert className="mt-3">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-xs">
                      {platform.note}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Credentials Dialog */}
      <Dialog open={credentialsDialog.open} onOpenChange={(open) => 
        setCredentialsDialog(prev => ({ ...prev, open }))
      }>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Connect {credentialsDialog.data?.platform && platforms.find(p => p.id === credentialsDialog.platform)?.name}
            </DialogTitle>
            <DialogDescription>
              {credentialsDialog.data?.instructions}
            </DialogDescription>
          </DialogHeader>
          
          {credentialsDialog.data && (
            <div className="space-y-4">
              {credentialsDialog.data.credentials_needed?.map((field) => (
                <div key={field}>
                  <Label htmlFor={field} className="capitalize">{field}</Label>
                  <Input
                    id={field}
                    type={field === 'password' ? 'password' : 'text'}
                    placeholder={`Enter your ${field}`}
                    value={credentials[field] || ''}
                    onChange={(e) => setCredentials(prev => ({
                      ...prev,
                      [field]: e.target.value
                    }))}
                  />
                </div>
              ))}
              
              {credentialsDialog.data.security_note && (
                <Alert>
                  <Shield className="h-4 w-4" />
                  <AlertDescription className="text-sm">
                    {credentialsDialog.data.security_note}
                  </AlertDescription>
                </Alert>
              )}
              
              <div className="flex space-x-2 pt-4">
                <Button
                  onClick={handleCredentialsSubmit}
                  disabled={!credentialsDialog.data.credentials_needed?.every(field => credentials[field])}
                  className="flex-1"
                >
                  Connect Platform
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setCredentialsDialog({ open: false, platform: null, data: null })}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Info Section */}
      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          How Platform Connections Work
        </h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
          <div>
            <h4 className="font-medium mb-1">OAuth Platforms (Facebook, eBay)</h4>
            <p>Secure OAuth authorization - we never store your password. You authorize our app directly through the platform.</p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Credential Platforms (OfferUp, Craigslist)</h4>
            <p>Encrypted credential storage - your login details are encrypted and stored securely for automated posting.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlatformConnections;