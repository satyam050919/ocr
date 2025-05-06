import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  Button,
  Paper,
  Stack
} from '@mui/material';
import { 
  FactCheck as ValidationIcon,
  LocalOffer as TaggingIcon,
  TextFields as ExtractionIcon,
  CallSplit as SplittingIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Document Validation',
      description: 'Validate documents against predefined rules and standards. Identify missing or invalid information.',
      icon: <ValidationIcon fontSize="large" color="primary" />,
      path: '/validation'
    },
    {
      title: 'Document Tagging',
      description: 'Automatically tag documents based on content, type, and metadata for better organization and retrieval.',
      icon: <TaggingIcon fontSize="large" color="primary" />,
      path: '/tagging'
    },
    {
      title: 'Attribute Extraction',
      description: 'Extract structured data from documents with confidence scores. Identify key information from various document types.',
      icon: <ExtractionIcon fontSize="large" color="primary" />,
      path: '/extraction'
    },
    {
      title: 'Document Splitting',
      description: 'Split multi-page documents into individual documents based on content type and classification.',
      icon: <SplittingIcon fontSize="large" color="primary" />,
      path: '/splitting'
    }
  ];

  return (
    <Box>
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          mb: 4, 
          borderRadius: 2,
          background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
          color: 'white'
        }}
      >
        <Typography variant="h4" gutterBottom>
          Document Processing System
        </Typography>
        <Typography variant="subtitle1">
          Upload, process, and extract information from documents using OCR and machine learning.
        </Typography>
        <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
          <Button 
            variant="contained" 
            color="secondary"
            onClick={() => navigate('/validation')}
          >
            Upload Document
          </Button>
          <Button 
            variant="outlined" 
            sx={{ color: 'white', borderColor: 'white' }}
          >
            View Documentation
          </Button>
        </Stack>
      </Paper>

      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Features
      </Typography>

      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={3} key={feature.title}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: '0.3s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 3
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" component="h2" gutterBottom align="center">
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  fullWidth
                  onClick={() => navigate(feature.path)}
                >
                  Go to {feature.title}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Dashboard;
