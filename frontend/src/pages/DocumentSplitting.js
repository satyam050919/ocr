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
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Stack,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Alert
} from '@mui/material';
import {
  CallSplit as SplitIcon,
  PictureAsPdf as PdfIcon,
  Image as ImageIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { z } from 'zod';
import DocumentUpload from '../components/DocumentUpload';

const splittingConfigSchema = z.object({
  split_method: z.enum([
    "document_type", 
    "page_count", 
    "content_based", 
    "form_detection", 
    "manual"
  ]),
  output_format: z.enum([
    "pdf", 
    "image", 
    "both"
  ]),
  naming_convention: z.string().min(1, "Naming convention is required"),
  min_confidence: z.number().min(0).max(1)
});

const documentTypes = [
  { value: 'passport', label: 'Passport' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'drivers_license', label: 'Driver\'s License' },
  { value: 'utility_bill', label: 'Utility Bill' },
  { value: 'bank_statement', label: 'Bank Statement' },
  { value: 'medical_record', label: 'Medical Record' },
  { value: 'legal_document', label: 'Legal Document' }
];

function DocumentSplitting() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [splitMethod, setSplitMethod] = useState('document_type');
  const [outputFormat, setOutputFormat] = useState('pdf');
  const [namingConvention, setNamingConvention] = useState('doc_{type}_{index}');
  const [minConfidence, setMinConfidence] = useState(0.7);
  const [splitDocuments, setSplitDocuments] = useState([]);
  const [preserveOriginal, setPreserveOriginal] = useState(true);
  
  const steps = ['Upload Document', 'Configure Splitting', 'Review Results'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setUploadedDocument(null);
    setSplitDocuments([]);
  };

  const handleUploadComplete = (data) => {
    setUploadedDocument(data);
    handleNext();
  };

  const handleSplitDocument = () => {
    const mockSplitDocs = [];
    
    if (splitMethod === 'document_type') {
      mockSplitDocs.push({
        id: 'doc_passport_1',
        name: 'doc_passport_1.pdf',
        type: 'passport',
        page_count: 1,
        confidence: 0.92,
        size: '245 KB',
        preview_url: 'https://example.com/preview/passport.jpg'
      });
      
      mockSplitDocs.push({
        id: 'doc_invoice_1',
        name: 'doc_invoice_1.pdf',
        type: 'invoice',
        page_count: 2,
        confidence: 0.87,
        size: '320 KB',
        preview_url: 'https://example.com/preview/invoice.jpg'
      });
      
      mockSplitDocs.push({
        id: 'doc_utility_bill_1',
        name: 'doc_utility_bill_1.pdf',
        type: 'utility_bill',
        page_count: 1,
        confidence: 0.85,
        size: '180 KB',
        preview_url: 'https://example.com/preview/utility_bill.jpg'
      });
    } else if (splitMethod === 'page_count') {
      for (let i = 1; i <= 5; i++) {
        mockSplitDocs.push({
          id: `doc_page_${i}`,
          name: `doc_page_${i}.pdf`,
          type: 'unknown',
          page_count: 1,
          confidence: 1.0,
          size: `${150 + Math.floor(Math.random() * 100)} KB`,
          preview_url: `https://example.com/preview/page_${i}.jpg`
        });
      }
    } else if (splitMethod === 'content_based') {
      mockSplitDocs.push({
        id: 'doc_personal_info',
        name: 'doc_personal_info.pdf',
        type: 'personal_info',
        page_count: 2,
        confidence: 0.88,
        size: '310 KB',
        preview_url: 'https://example.com/preview/personal_info.jpg'
      });
      
      mockSplitDocs.push({
        id: 'doc_financial',
        name: 'doc_financial.pdf',
        type: 'financial',
        page_count: 3,
        confidence: 0.82,
        size: '420 KB',
        preview_url: 'https://example.com/preview/financial.jpg'
      });
    } else {
      for (let i = 1; i <= 3; i++) {
        mockSplitDocs.push({
          id: `doc_${i}`,
          name: `doc_${i}.pdf`,
          type: 'unknown',
          page_count: 1,
          confidence: 0.75 + (Math.random() * 0.2),
          size: `${200 + Math.floor(Math.random() * 150)} KB`,
          preview_url: `https://example.com/preview/doc_${i}.jpg`
        });
      }
    }
    
    setSplitDocuments(mockSplitDocs);
    handleNext();
  };

  const handleDeleteSplitDocument = (docId) => {
    setSplitDocuments(splitDocuments.filter(doc => doc.id !== docId));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Splitting
      </Typography>
      <Typography variant="body1" paragraph>
        Split multi-page documents into individual documents based on content type and classification.
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
            <Typography variant="body2" color="text.secondary" paragraph>
              Upload a multi-page document (PDF) that you want to split into separate documents.
            </Typography>
            <DocumentUpload onUploadComplete={handleUploadComplete} />
          </Box>
        )}
        
        {activeStep === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Configure Splitting
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
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
                      Split Method
                    </Typography>
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel id="split-method-label">Split Method</InputLabel>
                      <Select
                        labelId="split-method-label"
                        value={splitMethod}
                        label="Split Method"
                        onChange={(e) => setSplitMethod(e.target.value)}
                      >
                        <MenuItem value="document_type">By Document Type</MenuItem>
                        <MenuItem value="page_count">By Page</MenuItem>
                        <MenuItem value="content_based">By Content</MenuItem>
                        <MenuItem value="form_detection">By Form Detection</MenuItem>
                        <MenuItem value="manual">Manual Split</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {splitMethod === 'document_type' && 
                        'Split the document based on detected document types (passport, invoice, etc.).'}
                      {splitMethod === 'page_count' && 
                        'Split the document into individual pages.'}
                      {splitMethod === 'content_based' && 
                        'Split the document based on content analysis and topic detection.'}
                      {splitMethod === 'form_detection' && 
                        'Split the document based on detected form boundaries.'}
                      {splitMethod === 'manual' && 
                        'Manually select pages to split into separate documents.'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Output Options
                    </Typography>
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel id="output-format-label">Output Format</InputLabel>
                      <Select
                        labelId="output-format-label"
                        value={outputFormat}
                        label="Output Format"
                        onChange={(e) => setOutputFormat(e.target.value)}
                      >
                        <MenuItem value="pdf">PDF</MenuItem>
                        <MenuItem value="image">Image (PNG/JPEG)</MenuItem>
                        <MenuItem value="both">Both PDF and Image</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <TextField
                      fullWidth
                      label="Naming Convention"
                      value={namingConvention}
                      onChange={(e) => setNamingConvention(e.target.value)}
                      helperText="Use {type}, {index}, {date} as placeholders"
                      sx={{ mb: 2 }}
                    />
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Minimum Confidence: {minConfidence}
                      </Typography>
                      <Box sx={{ px: 1 }}>
                        <Slider
                          value={minConfidence}
                          onChange={(e, newValue) => setMinConfidence(newValue)}
                          step={0.05}
                          marks
                          min={0}
                          max={1}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                        />
                      </Box>
                    </FormControl>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={preserveOriginal}
                          onChange={(e) => setPreserveOriginal(e.target.checked)}
                        />
                      }
                      label="Preserve original document"
                    />
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
                onClick={handleSplitDocument}
              >
                Split Document
              </Button>
            </Box>
          </Box>
        )}
        
        {activeStep === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Split Results
            </Typography>
            
            {splitDocuments.length === 0 ? (
              <Alert severity="warning" sx={{ mb: 3 }}>
                No documents were created during the splitting process. Try adjusting your splitting configuration.
              </Alert>
            ) : (
              <Alert severity="success" sx={{ mb: 3 }}>
                Successfully split into {splitDocuments.length} documents
              </Alert>
            )}
            
            <Grid container spacing={3}>
              {splitDocuments.map((doc) => (
                <Grid item xs={12} sm={6} md={4} key={doc.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        {doc.name.endsWith('.pdf') ? (
                          <PdfIcon fontSize="large" color="primary" sx={{ mr: 1 }} />
                        ) : (
                          <ImageIcon fontSize="large" color="primary" sx={{ mr: 1 }} />
                        )}
                        <Typography variant="subtitle1" noWrap>
                          {doc.name}
                        </Typography>
                      </Box>
                      
                      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                        <Chip 
                          size="small" 
                          label={doc.type.replace('_', ' ')}
                          color="primary"
                          sx={{ textTransform: 'capitalize' }}
                        />
                        <Chip 
                          size="small" 
                          label={`${doc.page_count} page${doc.page_count > 1 ? 's' : ''}`}
                          variant="outlined"
                        />
                        <Chip 
                          size="small" 
                          label={`${Math.round(doc.confidence * 100)}%`}
                          color={doc.confidence > 0.8 ? "success" : "default"}
                          variant="outlined"
                        />
                      </Stack>
                      
                      <Typography variant="body2" color="text.secondary">
                        Size: {doc.size}
                      </Typography>
                    </CardContent>
                    <Divider />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 1 }}>
                      <Tooltip title="View document">
                        <IconButton size="small">
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download document">
                        <IconButton size="small" color="primary">
                          <DownloadIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete document">
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={() => handleDeleteSplitDocument(doc.id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
            
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

export default DocumentSplitting;
