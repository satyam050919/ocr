import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar
} from '@mui/material';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const apiSettingsSchema = z.object({
  api_url: z.string().url("Must be a valid URL"),
  api_key: z.string().min(1, "API key is required"),
  timeout: z.number().int().min(1000).max(60000),
  max_retries: z.number().int().min(0).max(10)
});

const ocrSettingsSchema = z.object({
  default_engine: z.enum(["textract", "tesseract", "auto"]),
  enhanced_features: z.boolean(),
  confidence_threshold: z.number().min(0).max(1),
  language: z.string().min(1, "Language is required")
});

const storageSettingsSchema = z.object({
  storage_type: z.enum(["s3", "local", "database"]),
  s3_bucket: z.string().optional(),
  local_path: z.string().optional(),
  retention_days: z.number().int().min(1).max(365)
});

function Settings() {
  const [activeTab, setActiveTab] = useState('api');
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const { 
    register: registerApi, 
    handleSubmit: handleSubmitApi, 
    formState: { errors: errorsApi } 
  } = useForm({
    resolver: zodResolver(apiSettingsSchema),
    defaultValues: {
      api_url: 'https://api.example.com/v1',
      api_key: 'sk_test_123456789',
      timeout: 30000,
      max_retries: 3
    }
  });
  
  const { 
    register: registerOcr, 
    handleSubmit: handleSubmitOcr, 
    formState: { errors: errorsOcr } 
  } = useForm({
    resolver: zodResolver(ocrSettingsSchema),
    defaultValues: {
      default_engine: 'textract',
      enhanced_features: true,
      confidence_threshold: 0.7,
      language: 'en'
    }
  });
  
  const { 
    register: registerStorage, 
    handleSubmit: handleSubmitStorage, 
    formState: { errors: errorsStorage } 
  } = useForm({
    resolver: zodResolver(storageSettingsSchema),
    defaultValues: {
      storage_type: 's3',
      s3_bucket: 'document-processing-bucket',
      local_path: '/data/documents',
      retention_days: 30
    }
  });

  const onSubmitApi = (data) => {
    console.log('API Settings:', data);
    setSaveSuccess(true);
  };
  
  const onSubmitOcr = (data) => {
    console.log('OCR Settings:', data);
    setSaveSuccess(true);
  };
  
  const onSubmitStorage = (data) => {
    console.log('Storage Settings:', data);
    setSaveSuccess(true);
  };

  const handleCloseSnackbar = () => {
    setSaveSuccess(false);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" paragraph>
        Configure the document processing system settings.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Settings Categories
            </Typography>
            <List component="nav">
              <ListItem 
                button 
                selected={activeTab === 'api'} 
                onClick={() => setActiveTab('api')}
              >
                <ListItemText primary="API Configuration" />
              </ListItem>
              <ListItem 
                button 
                selected={activeTab === 'ocr'} 
                onClick={() => setActiveTab('ocr')}
              >
                <ListItemText primary="OCR Settings" />
              </ListItem>
              <ListItem 
                button 
                selected={activeTab === 'storage'} 
                onClick={() => setActiveTab('storage')}
              >
                <ListItemText primary="Storage Settings" />
              </ListItem>
              <ListItem 
                button 
                selected={activeTab === 'validation'} 
                onClick={() => setActiveTab('validation')}
              >
                <ListItemText primary="Validation Rules" />
              </ListItem>
              <ListItem 
                button 
                selected={activeTab === 'notifications'} 
                onClick={() => setActiveTab('notifications')}
              >
                <ListItemText primary="Notifications" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={9}>
          <Paper sx={{ p: 3 }}>
            {activeTab === 'api' && (
              <Box component="form" onSubmit={handleSubmitApi(onSubmitApi)}>
                <Typography variant="h6" gutterBottom>
                  API Configuration
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Configure the API endpoints and authentication settings.
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="API URL"
                      {...registerApi('api_url')}
                      error={!!errorsApi.api_url}
                      helperText={errorsApi.api_url?.message}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="API Key"
                      type="password"
                      {...registerApi('api_key')}
                      error={!!errorsApi.api_key}
                      helperText={errorsApi.api_key?.message}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Timeout (ms)"
                      type="number"
                      {...registerApi('timeout')}
                      error={!!errorsApi.timeout}
                      helperText={errorsApi.timeout?.message}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Max Retries"
                      type="number"
                      {...registerApi('max_retries')}
                      error={!!errorsApi.max_retries}
                      helperText={errorsApi.max_retries?.message}
                    />
                  </Grid>
                </Grid>
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                  >
                    Save API Settings
                  </Button>
                </Box>
              </Box>
            )}
            
            {activeTab === 'ocr' && (
              <Box component="form" onSubmit={handleSubmitOcr(onSubmitOcr)}>
                <Typography variant="h6" gutterBottom>
                  OCR Settings
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Configure OCR engines and processing options.
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <FormControl fullWidth error={!!errorsOcr.default_engine}>
                      <InputLabel id="default-engine-label">Default OCR Engine</InputLabel>
                      <Select
                        labelId="default-engine-label"
                        label="Default OCR Engine"
                        {...registerOcr('default_engine')}
                      >
                        <MenuItem value="textract">AWS Textract</MenuItem>
                        <MenuItem value="tesseract">Tesseract OCR</MenuItem>
                        <MenuItem value="auto">Auto (Smart Selection)</MenuItem>
                      </Select>
                      {errorsOcr.default_engine && (
                        <Typography variant="caption" color="error">
                          {errorsOcr.default_engine.message}
                        </Typography>
                      )}
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          {...registerOcr('enhanced_features')}
                          defaultChecked
                        />
                      }
                      label="Enable Enhanced Features (Tables, Forms, Queries)"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="body2" gutterBottom>
                      Confidence Threshold
                    </Typography>
                    <Box sx={{ px: 1 }}>
                      <Slider
                        {...registerOcr('confidence_threshold')}
                        step={0.05}
                        marks
                        min={0}
                        max={1}
                        valueLabelDisplay="auto"
                        valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                      />
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControl fullWidth error={!!errorsOcr.language}>
                      <InputLabel id="language-label">Primary Language</InputLabel>
                      <Select
                        labelId="language-label"
                        label="Primary Language"
                        {...registerOcr('language')}
                      >
                        <MenuItem value="en">English</MenuItem>
                        <MenuItem value="es">Spanish</MenuItem>
                        <MenuItem value="fr">French</MenuItem>
                        <MenuItem value="de">German</MenuItem>
                        <MenuItem value="it">Italian</MenuItem>
                        <MenuItem value="pt">Portuguese</MenuItem>
                        <MenuItem value="zh">Chinese</MenuItem>
                        <MenuItem value="ja">Japanese</MenuItem>
                      </Select>
                      {errorsOcr.language && (
                        <Typography variant="caption" color="error">
                          {errorsOcr.language.message}
                        </Typography>
                      )}
                    </FormControl>
                  </Grid>
                </Grid>
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                  >
                    Save OCR Settings
                  </Button>
                </Box>
              </Box>
            )}
            
            {activeTab === 'storage' && (
              <Box component="form" onSubmit={handleSubmitStorage(onSubmitStorage)}>
                <Typography variant="h6" gutterBottom>
                  Storage Settings
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Configure document storage options and retention policies.
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <FormControl fullWidth error={!!errorsStorage.storage_type}>
                      <InputLabel id="storage-type-label">Storage Type</InputLabel>
                      <Select
                        labelId="storage-type-label"
                        label="Storage Type"
                        {...registerStorage('storage_type')}
                      >
                        <MenuItem value="s3">Amazon S3</MenuItem>
                        <MenuItem value="local">Local Storage</MenuItem>
                        <MenuItem value="database">Database Storage</MenuItem>
                      </Select>
                      {errorsStorage.storage_type && (
                        <Typography variant="caption" color="error">
                          {errorsStorage.storage_type.message}
                        </Typography>
                      )}
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="S3 Bucket Name"
                      {...registerStorage('s3_bucket')}
                      error={!!errorsStorage.s3_bucket}
                      helperText={errorsStorage.s3_bucket?.message}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Local Storage Path"
                      {...registerStorage('local_path')}
                      error={!!errorsStorage.local_path}
                      helperText={errorsStorage.local_path?.message}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Retention Period (days)"
                      type="number"
                      {...registerStorage('retention_days')}
                      error={!!errorsStorage.retention_days}
                      helperText={errorsStorage.retention_days?.message}
                    />
                  </Grid>
                </Grid>
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                  >
                    Save Storage Settings
                  </Button>
                </Box>
              </Box>
            )}
            
            {activeTab === 'validation' && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Validation Rules
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Configure document validation rules and hardblocks.
                </Typography>
                
                <Alert severity="info" sx={{ mb: 3 }}>
                  This section allows you to configure validation rules for different document types.
                  You can set up hardblocks for critical fields and warnings for less critical fields.
                </Alert>
                
                <Typography variant="subtitle1" gutterBottom>
                  Coming Soon
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  The validation rules configuration interface is under development and will be available soon.
                </Typography>
              </Box>
            )}
            
            {activeTab === 'notifications' && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Notifications
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Configure notification settings for document processing events.
                </Typography>
                
                <Alert severity="info" sx={{ mb: 3 }}>
                  This section allows you to configure notifications for document processing events,
                  such as validation failures, processing completions, and system errors.
                </Alert>
                
                <Typography variant="subtitle1" gutterBottom>
                  Coming Soon
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  The notifications configuration interface is under development and will be available soon.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      <Snackbar
        open={saveSuccess}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Settings saved successfully!
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Settings;
