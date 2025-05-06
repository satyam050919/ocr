import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Stepper,
  Step,
  StepLabel,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  IconButton,
  InputAdornment
} from '@mui/material';
import {
  LocalOffer as TagIcon,
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { z } from 'zod';
import DocumentUpload from '../components/DocumentUpload';

const tagSchema = z.object({
  name: z.string().min(1, "Tag name is required"),
  category: z.enum([
    "document_type", 
    "content", 
    "metadata", 
    "security", 
    "quality", 
    "custom"
  ]),
  confidence: z.number().min(0).max(1),
  source: z.enum(["rule", "ml", "manual", "rule,ml", "ml,rule"]),
});

const tagCategories = {
  document_type: { color: 'primary', label: 'Document Type' },
  content: { color: 'secondary', label: 'Content' },
  metadata: { color: 'info', label: 'Metadata' },
  security: { color: 'error', label: 'Security' },
  quality: { color: 'warning', label: 'Quality' },
  custom: { color: 'default', label: 'Custom' }
};

function DocumentTagging() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [tags, setTags] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  const steps = ['Upload Document', 'Document Tagging', 'Review Tags'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setUploadedDocument(null);
    setTags([]);
  };

  const handleUploadComplete = (data) => {
    setUploadedDocument(data);
    
    const mockTags = [
      {
        name: 'passport',
        category: 'document_type',
        confidence: 0.95,
        source: 'rule',
        metadata: { matches: 3, rule_pattern: 'passport' }
      },
      {
        name: 'expiration',
        category: 'content',
        confidence: 0.87,
        source: 'rule',
        metadata: { matches: 2, rule_pattern: 'expir' }
      },
      {
        name: 'nationality',
        category: 'content',
        confidence: 0.82,
        source: 'rule',
        metadata: { matches: 1, rule_pattern: 'nationality' }
      },
      {
        name: 'personal',
        category: 'content',
        confidence: 0.78,
        source: 'ml',
        metadata: { frequency: 5, score: 0.78 }
      },
      {
        name: 'identification',
        category: 'content',
        confidence: 0.75,
        source: 'ml',
        metadata: { frequency: 4, score: 0.75 }
      },
      {
        name: 'travel',
        category: 'content',
        confidence: 0.72,
        source: 'ml',
        metadata: { frequency: 3, score: 0.72 }
      },
      {
        name: 'official document',
        category: 'content',
        confidence: 0.68,
        source: 'ml',
        metadata: { frequency: 2, score: 0.68, type: 'bigram' }
      },
      {
        name: 'confidential',
        category: 'security',
        confidence: 0.65,
        source: 'rule',
        metadata: { matches: 1, rule_pattern: 'confidential' }
      },
      {
        name: 'government',
        category: 'metadata',
        confidence: 0.62,
        source: 'ml',
        metadata: { frequency: 2, score: 0.62 }
      },
      {
        name: 'international',
        category: 'content',
        confidence: 0.58,
        source: 'ml',
        metadata: { frequency: 1, score: 0.58 }
      }
    ];
    
    setTags(mockTags);
    handleNext();
  };

  const handleAddTag = () => {
    const newTag = {
      name: 'custom tag',
      category: 'custom',
      confidence: 1.0,
      source: 'manual',
      metadata: { added_by: 'user', timestamp: new Date().toISOString() }
    };
    
    setTags([...tags, newTag]);
  };

  const filteredTags = tags.filter(tag => {
    const matchesSearch = searchQuery === '' || 
      tag.name.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || 
      tag.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const sortedTags = [...filteredTags].sort((a, b) => b.confidence - a.confidence);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Tagging
      </Typography>
      <Typography variant="body1" paragraph>
        Automatically tag documents based on content, type, and metadata for better organization and retrieval.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {activeStep === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Upload Document
            </Typography>
            <DocumentUpload onUploadComplete={handleUploadComplete} />
          </Box>
        )}
        
        {activeStep === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Document Tagging
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Document Information
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="body2" sx={{ mr: 1, fontWeight: 'bold' }}>
                        File:
                      </Typography>
                      <Typography variant="body2">
                        {uploadedDocument?.file_path.split('/').pop() || 'Document'}
                      </Typography>
                    </Box>
                    
                    <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                      Tag Statistics
                    </Typography>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap' }}>
                      <Box sx={{ textAlign: 'center', mb: 1 }}>
                        <Typography variant="h5" color="primary.main">
                          {tags.length}
                        </Typography>
                        <Typography variant="body2">Total Tags</Typography>
                      </Box>
                      
                      <Box sx={{ textAlign: 'center', mb: 1 }}>
                        <Typography variant="h5" color="secondary.main">
                          {tags.filter(t => t.source.includes('ml')).length}
                        </Typography>
                        <Typography variant="body2">ML Tags</Typography>
                      </Box>
                      
                      <Box sx={{ textAlign: 'center', mb: 1 }}>
                        <Typography variant="h5" color="info.main">
                          {tags.filter(t => t.source.includes('rule')).length}
                        </Typography>
                        <Typography variant="body2">Rule Tags</Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
                
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Filter Tags
                    </Typography>
                    
                    <TextField
                      fullWidth
                      placeholder="Search tags..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      sx={{ mb: 2 }}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon />
                          </InputAdornment>
                        ),
                      }}
                    />
                    
                    <Typography variant="body2" gutterBottom>
                      Filter by Category:
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      <Chip
                        label="All"
                        onClick={() => setSelectedCategory('all')}
                        color={selectedCategory === 'all' ? 'primary' : 'default'}
                      />
                      
                      {Object.entries(tagCategories).map(([key, { color, label }]) => (
                        <Chip
                          key={key}
                          label={label}
                          onClick={() => setSelectedCategory(key)}
                          color={selectedCategory === key ? color : 'default'}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={8}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle1">
                        Document Tags
                      </Typography>
                      
                      <Button
                        variant="outlined"
                        startIcon={<AddIcon />}
                        size="small"
                        onClick={handleAddTag}
                      >
                        Add Tag
                      </Button>
                    </Box>
                    
                    <List>
                      {sortedTags.map((tag, index) => {
                        const categoryInfo = tagCategories[tag.category] || tagCategories.custom;
                        
                        return (
                          <React.Fragment key={`${tag.name}-${index}`}>
                            <ListItem
                              secondaryAction={
                                <Chip
                                  size="small"
                                  label={`${Math.round(tag.confidence * 100)}%`}
                                  color={tag.confidence > 0.8 ? 'success' : tag.confidence > 0.6 ? 'info' : 'default'}
                                />
                              }
                            >
                              <ListItemText
                                primary={
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <Chip
                                      size="small"
                                      label={tag.name}
                                      icon={<TagIcon />}
                                      sx={{ mr: 1 }}
                                    />
                                    <Chip
                                      size="small"
                                      label={categoryInfo.label}
                                      color={categoryInfo.color}
                                      variant="outlined"
                                      sx={{ mr: 1 }}
                                    />
                                    <Chip
                                      size="small"
                                      label={tag.source}
                                      variant="outlined"
                                    />
                                  </Box>
                                }
                                secondary={
                                  <Typography variant="caption" color="text.secondary">
                                    {tag.metadata && tag.source.includes('rule') && 
                                      `Rule pattern: "${tag.metadata.rule_pattern}", Matches: ${tag.metadata.matches}`}
                                    {tag.metadata && tag.source.includes('ml') && 
                                      `Frequency: ${tag.metadata.frequency}, Score: ${tag.metadata.score.toFixed(2)}`}
                                    {tag.metadata && tag.source === 'manual' && 
                                      `Added manually by user`}
                                  </Typography>
                                }
                              />
                            </ListItem>
                            {index < sortedTags.length - 1 && <Divider />}
                          </React.Fragment>
                        );
                      })}
                      
                      {sortedTags.length === 0 && (
                        <ListItem>
                          <ListItemText
                            primary="No tags found"
                            secondary="Try adjusting your filters or add a custom tag"
                          />
                        </ListItem>
                      )}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
              <Button onClick={handleBack} sx={{ mr: 1 }}>
                Back
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
              >
                Review Tags
              </Button>
            </Box>
          </Box>
        )}
        
        {activeStep === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Tags
            </Typography>
            
            <Card variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>
                  Tag Summary
                </Typography>
                
                <Grid container spacing={2}>
                  {Object.entries(tagCategories).map(([category, { color, label }]) => {
                    const categoryTags = tags.filter(tag => tag.category === category);
                    if (categoryTags.length === 0) return null;
                    
                    return (
                      <Grid item xs={12} sm={6} md={4} key={category}>
                        <Paper variant="outlined" sx={{ p: 2 }}>
                          <Typography variant="subtitle2" color={`${color}.main`} gutterBottom>
                            {label}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {categoryTags.map((tag, index) => (
                              <Chip
                                key={`${tag.name}-${index}`}
                                size="small"
                                label={tag.name}
                                color={color}
                                variant={tag.confidence > 0.7 ? "default" : "outlined"}
                              />
                            ))}
                          </Box>
                        </Paper>
                      </Grid>
                    );
                  })}
                </Grid>
              </CardContent>
            </Card>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
              <Button onClick={handleBack} sx={{ mr: 1 }}>
                Back
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleReset}
              >
                Process Another Document
              </Button>
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
}

export default DocumentTagging;
