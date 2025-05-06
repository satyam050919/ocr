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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  TextFields as ExtractionIcon,
  ContentCopy as CopyIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { z } from 'zod';
import DocumentUpload from '../components/DocumentUpload';

const attributeSchema = z.object({
  name: z.string().min(1, "Attribute name is required"),
  value: z.string().min(1, "Attribute value is required"),
  type: z.enum([
    "text", 
    "date", 
    "number", 
    "currency", 
    "percentage", 
    "boolean", 
    "id", 
    "name", 
    "address", 
    "phone", 
    "email", 
    "custom"
  ]),
  confidence: z.number().min(0).max(1),
  extraction_method: z.enum([
    "regex", 
    "keyword", 
    "position", 
    "table", 
    "form", 
    "ml", 
    "custom"
  ]),
});

const attributeTypes = {
  text: { color: 'default', label: 'Text' },
  date: { color: 'primary', label: 'Date' },
  number: { color: 'secondary', label: 'Number' },
  currency: { color: 'success', label: 'Currency' },
  percentage: { color: 'info', label: 'Percentage' },
  boolean: { color: 'warning', label: 'Boolean' },
  id: { color: 'error', label: 'ID' },
  name: { color: 'primary', label: 'Name' },
  address: { color: 'secondary', label: 'Address' },
  phone: { color: 'success', label: 'Phone' },
  email: { color: 'info', label: 'Email' },
  custom: { color: 'default', label: 'Custom' }
};

const documentTypes = [
  { value: 'passport', label: 'Passport' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'drivers_license', label: 'Driver\'s License' },
  { value: 'utility_bill', label: 'Utility Bill' },
  { value: 'bank_statement', label: 'Bank Statement' },
  { value: 'medical_record', label: 'Medical Record' },
  { value: 'legal_document', label: 'Legal Document' }
];

function AttributeExtraction() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [documentType, setDocumentType] = useState('passport');
  const [attributes, setAttributes] = useState([]);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  
  const steps = ['Upload Document', 'Configure Extraction', 'View Attributes'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setUploadedDocument(null);
    setAttributes([]);
  };

  const handleUploadComplete = (data) => {
    setUploadedDocument(data);
    handleNext();
  };

  const handleExtractAttributes = () => {
    let mockAttributes = [];
    
    if (documentType === 'passport') {
      mockAttributes = [
        {
          name: 'passport_number',
          value: 'AB123456',
          type: 'id',
          confidence: 0.95,
          extraction_method: 'regex',
          metadata: { match_position: 120, match_length: 8, full_match: 'Passport No: AB123456' }
        },
        {
          name: 'full_name',
          value: 'John Smith',
          type: 'name',
          confidence: 0.92,
          extraction_method: 'regex',
          metadata: { match_position: 85, match_length: 15, full_match: 'Name: John Smith' }
        },
        {
          name: 'date_of_birth',
          value: '15/04/1985',
          type: 'date',
          confidence: 0.88,
          extraction_method: 'regex',
          metadata: { match_position: 150, match_length: 20, full_match: 'Date of Birth: 15/04/1985' }
        },
        {
          name: 'nationality',
          value: 'United States',
          type: 'text',
          confidence: 0.85,
          extraction_method: 'regex',
          metadata: { match_position: 180, match_length: 25, full_match: 'Nationality: United States' }
        },
        {
          name: 'expiry_date',
          value: '20/06/2030',
          type: 'date',
          confidence: 0.87,
          extraction_method: 'regex',
          metadata: { match_position: 210, match_length: 25, full_match: 'Expiry Date: 20/06/2030' }
        },
        {
          name: 'mrz_line1',
          value: 'P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<',
          type: 'text',
          confidence: 0.78,
          extraction_method: 'regex',
          metadata: { match_position: 300, match_length: 44, full_match: 'P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<' }
        },
        {
          name: 'mrz_line2',
          value: 'AB123456<0USA8504159M3006208<<<<<<<<<<<<<<',
          type: 'text',
          confidence: 0.76,
          extraction_method: 'regex',
          metadata: { match_position: 344, match_length: 44, full_match: 'AB123456<0USA8504159M3006208<<<<<<<<<<<<<<' }
        },
        {
          name: 'gender',
          value: 'M',
          type: 'text',
          confidence: 0.65,
          extraction_method: 'ml',
          metadata: { confidence_score: 0.65 }
        }
      ];
    } else if (documentType === 'invoice') {
      mockAttributes = [
        {
          name: 'invoice_number',
          value: 'INV-2023-0042',
          type: 'id',
          confidence: 0.94,
          extraction_method: 'regex',
          metadata: { match_position: 120, match_length: 13, full_match: 'Invoice #: INV-2023-0042' }
        },
        {
          name: 'invoice_date',
          value: '05/01/2023',
          type: 'date',
          confidence: 0.91,
          extraction_method: 'regex',
          metadata: { match_position: 150, match_length: 20, full_match: 'Date: 05/01/2023' }
        },
        {
          name: 'due_date',
          value: '04/02/2023',
          type: 'date',
          confidence: 0.89,
          extraction_method: 'regex',
          metadata: { match_position: 180, match_length: 25, full_match: 'Due Date: 04/02/2023' }
        },
        {
          name: 'total_amount',
          value: '1,250.00',
          type: 'currency',
          confidence: 0.93,
          extraction_method: 'regex',
          metadata: { match_position: 300, match_length: 20, full_match: 'Total: $1,250.00' }
        },
        {
          name: 'tax_amount',
          value: '125.00',
          type: 'currency',
          confidence: 0.87,
          extraction_method: 'regex',
          metadata: { match_position: 280, match_length: 15, full_match: 'Tax: $125.00' }
        },
        {
          name: 'vendor_name',
          value: 'ABC Corporation',
          type: 'name',
          confidence: 0.82,
          extraction_method: 'keyword',
          metadata: { keyword: 'from', line_number: 5, context_line: 'From: ABC Corporation' }
        },
        {
          name: 'customer_name',
          value: 'XYZ Company',
          type: 'name',
          confidence: 0.79,
          extraction_method: 'keyword',
          metadata: { keyword: 'to', line_number: 8, context_line: 'Bill To: XYZ Company' }
        },
        {
          name: 'payment_terms',
          value: 'Net 30',
          type: 'text',
          confidence: 0.72,
          extraction_method: 'ml',
          metadata: { confidence_score: 0.72 }
        }
      ];
    } else if (documentType === 'drivers_license') {
      mockAttributes = [
        {
          name: 'license_number',
          value: 'DL12345678',
          type: 'id',
          confidence: 0.93,
          extraction_method: 'regex',
          metadata: { match_position: 120, match_length: 10, full_match: 'DL: DL12345678' }
        },
        {
          name: 'full_name',
          value: 'Jane Doe',
          type: 'name',
          confidence: 0.91,
          extraction_method: 'regex',
          metadata: { match_position: 85, match_length: 13, full_match: 'Name: Jane Doe' }
        },
        {
          name: 'date_of_birth',
          value: '22/07/1990',
          type: 'date',
          confidence: 0.89,
          extraction_method: 'regex',
          metadata: { match_position: 150, match_length: 20, full_match: 'DOB: 22/07/1990' }
        },
        {
          name: 'address',
          value: '123 Main St, Anytown, CA 12345',
          type: 'address',
          confidence: 0.84,
          extraction_method: 'regex',
          metadata: { match_position: 180, match_length: 35, full_match: 'Address: 123 Main St, Anytown, CA 12345' }
        },
        {
          name: 'issue_date',
          value: '10/03/2020',
          type: 'date',
          confidence: 0.86,
          extraction_method: 'regex',
          metadata: { match_position: 220, match_length: 20, full_match: 'Issue Date: 10/03/2020' }
        },
        {
          name: 'expiry_date',
          value: '22/07/2028',
          type: 'date',
          confidence: 0.87,
          extraction_method: 'regex',
          metadata: { match_position: 250, match_length: 20, full_match: 'Exp: 22/07/2028' }
        },
        {
          name: 'class',
          value: 'C',
          type: 'text',
          confidence: 0.92,
          extraction_method: 'regex',
          metadata: { match_position: 280, match_length: 8, full_match: 'Class: C' }
        },
        {
          name: 'restrictions',
          value: 'B',
          type: 'text',
          confidence: 0.68,
          extraction_method: 'ml',
          metadata: { confidence_score: 0.68 }
        }
      ];
    } else {
      mockAttributes = [
        {
          name: 'document_id',
          value: `DOC-${Math.floor(Math.random() * 10000)}`,
          type: 'id',
          confidence: 0.85,
          extraction_method: 'regex',
          metadata: { match_position: 120, match_length: 10 }
        },
        {
          name: 'date',
          value: '15/05/2023',
          type: 'date',
          confidence: 0.82,
          extraction_method: 'regex',
          metadata: { match_position: 150, match_length: 10 }
        },
        {
          name: 'name',
          value: 'Sample Name',
          type: 'name',
          confidence: 0.78,
          extraction_method: 'keyword',
          metadata: { keyword: 'name', line_number: 5 }
        },
        {
          name: 'amount',
          value: '500.00',
          type: 'currency',
          confidence: 0.75,
          extraction_method: 'regex',
          metadata: { match_position: 200, match_length: 6 }
        }
      ];
    }
    
    mockAttributes = mockAttributes.map(attr => ({
      ...attr,
      confidence: Math.max(0.1, Math.min(0.99, attr.confidence + (Math.random() * 0.1 - 0.05)))
    }));
    
    setAttributes(mockAttributes);
    handleNext();
  };

  const filteredAttributes = attributes.filter(attr => attr.confidence >= confidenceThreshold);
  
  const sortedAttributes = [...filteredAttributes].sort((a, b) => b.confidence - a.confidence);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Attribute Extraction
      </Typography>
      <Typography variant="body1" paragraph>
        Extract structured data from documents with confidence scores. Identify key information from various document types.
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
              Configure Extraction
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
                      Document Type
                    </Typography>
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel id="document-type-label">Document Type</InputLabel>
                      <Select
                        labelId="document-type-label"
                        value={documentType}
                        label="Document Type"
                        onChange={(e) => setDocumentType(e.target.value)}
                      >
                        {documentTypes.map((type) => (
                          <MenuItem key={type.value} value={type.value}>
                            {type.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Extraction Options
                    </Typography>
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Confidence Threshold: {confidenceThreshold}
                      </Typography>
                      <Box sx={{ px: 1 }}>
                        <Slider
                          value={confidenceThreshold}
                          onChange={(e, newValue) => setConfidenceThreshold(newValue)}
                          step={0.05}
                          marks
                          min={0}
                          max={1}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                        />
                      </Box>
                    </FormControl>
                    
                    <Typography variant="body2" gutterBottom>
                      Extraction Methods:
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      <Chip label="Regex" color="primary" />
                      <Chip label="Keyword" color="secondary" />
                      <Chip label="Position" color="info" />
                      <Chip label="Table" color="success" />
                      <Chip label="Form" color="warning" />
                      <Chip label="ML" color="error" />
                    </Box>
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
                onClick={handleExtractAttributes}
              >
                Extract Attributes
              </Button>
            </Box>
          </Box>
        )}
        
        {activeStep === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Extracted Attributes
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" gutterBottom>
                Confidence Threshold: {confidenceThreshold}
              </Typography>
              <Box sx={{ px: 1, mb: 2 }}>
                <Slider
                  value={confidenceThreshold}
                  onChange={(e, newValue) => setConfidenceThreshold(newValue)}
                  step={0.05}
                  marks
                  min={0}
                  max={1}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                />
              </Box>
              
              <Typography variant="body2" color="text.secondary">
                Showing {filteredAttributes.length} of {attributes.length} attributes (filtered by confidence threshold)
              </Typography>
            </Box>
            
            <TableContainer component={Paper} variant="outlined">
              <Table sx={{ minWidth: 650 }} size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Attribute</TableCell>
                    <TableCell>Value</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Method</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedAttributes.map((attr, index) => {
                    const typeInfo = attributeTypes[attr.type] || attributeTypes.custom;
                    
                    return (
                      <TableRow
                        key={`${attr.name}-${index}`}
                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                      >
                        <TableCell component="th" scope="row">
                          {attr.name.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>{attr.value}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={typeInfo.label}
                            color={typeInfo.color}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Box sx={{ width: '100%', mr: 1 }}>
                              <LinearProgress 
                                variant="determinate" 
                                value={attr.confidence * 100} 
                                color={attr.confidence > 0.8 ? "success" : attr.confidence > 0.6 ? "info" : attr.confidence > 0.4 ? "warning" : "error"}
                                sx={{ height: 8, borderRadius: 5 }}
                              />
                            </Box>
                            <Box sx={{ minWidth: 35 }}>
                              <Typography variant="body2" color="text.secondary">
                                {`${Math.round(attr.confidence * 100)}%`}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={attr.extraction_method}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Copy value">
                            <IconButton size="small">
                              <CopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View details">
                            <IconButton size="small">
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                  
                  {sortedAttributes.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No attributes found with the current confidence threshold. Try lowering the threshold.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            
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

export default AttributeExtraction;
