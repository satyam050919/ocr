import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Stepper,
  Step,
  StepLabel,
  Button,
  Divider,
  Alert,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as ValidIcon,
  Description as DocumentIcon
} from '@mui/icons-material';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import DocumentUpload from '../components/DocumentUpload';

const documentValidationSchema = z.object({
  document_id: z.string().min(1, "Document ID is required"),
  document_type: z.enum([
    "passport", 
    "invoice", 
    "drivers_license", 
    "utility_bill", 
    "bank_statement", 
    "medical_record", 
    "legal_document", 
    "unknown"
  ]),
  validation_rules: z.array(
    z.object({
      field: z.string(),
      rule: z.string(),
      severity: z.enum(["error", "warning", "info"])
    })
  ).optional()
});

const validationRules = {
  passport: [
    { field: "passport_number", rule: "required", severity: "error" },
    { field: "full_name", rule: "required", severity: "error" },
    { field: "date_of_birth", rule: "required", severity: "error" },
    { field: "expiry_date", rule: "required", severity: "error" },
    { field: "mrz", rule: "valid_format", severity: "error" },
    { field: "photo", rule: "clear_image", severity: "warning" }
  ],
  invoice: [
    { field: "invoice_number", rule: "required", severity: "error" },
    { field: "invoice_date", rule: "required", severity: "error" },
    { field: "total_amount", rule: "required", severity: "error" },
    { field: "vendor_name", rule: "required", severity: "error" },
    { field: "line_items", rule: "at_least_one", severity: "warning" }
  ],
  drivers_license: [
    { field: "license_number", rule: "required", severity: "error" },
    { field: "full_name", rule: "required", severity: "error" },
    { field: "date_of_birth", rule: "required", severity: "error" },
    { field: "expiry_date", rule: "required", severity: "error" },
    { field: "address", rule: "required", severity: "error" },
    { field: "photo", rule: "clear_image", severity: "warning" }
  ],
  utility_bill: [
    { field: "account_number", rule: "required", severity: "error" },
    { field: "bill_date", rule: "required", severity: "error" },
    { field: "total_amount", rule: "required", severity: "error" },
    { field: "customer_name", rule: "required", severity: "error" },
    { field: "service_address", rule: "required", severity: "error" }
  ],
  bank_statement: [
    { field: "account_number", rule: "required", severity: "error" },
    { field: "statement_date", rule: "required", severity: "error" },
    { field: "opening_balance", rule: "required", severity: "error" },
    { field: "closing_balance", rule: "required", severity: "error" },
    { field: "customer_name", rule: "required", severity: "error" }
  ]
};

function DocumentValidation() {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const [hardBlocks, setHardBlocks] = useState([]);
  const [warnings, setWarnings] = useState([]);
  
  const { register, handleSubmit, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(documentValidationSchema),
    defaultValues: {
      document_type: "passport",
      validation_rules: []
    }
  });

  const steps = ['Upload Document', 'Configure Validation', 'Validation Results'];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setUploadedDocument(null);
    setValidationResults(null);
    setHardBlocks([]);
    setWarnings([]);
  };

  const handleUploadComplete = (data) => {
    setUploadedDocument(data);
    handleNext();
  };

  const onSubmitValidationConfig = (data) => {
    const rules = validationRules[data.document_type] || [];
    
    const mockResults = {
      document_id: data.document_id,
      document_type: data.document_type,
      validation_passed: Math.random() > 0.3, // Random pass/fail for demo
      fields: []
    };
    
    const mockHardBlocks = [];
    const mockWarnings = [];
    
    rules.forEach(rule => {
      const passed = Math.random() > 0.3; // Random pass/fail for demo
      
      const fieldResult = {
        field: rule.field,
        rule: rule.rule,
        passed: passed,
        severity: rule.severity,
        confidence: passed ? 0.8 + (Math.random() * 0.2) : 0.3 + (Math.random() * 0.5),
        message: passed 
          ? `${rule.field} validation passed` 
          : `${rule.field} failed ${rule.rule} validation`
      };
      
      mockResults.fields.push(fieldResult);
      
      if (!passed) {
        if (rule.severity === 'error') {
          mockHardBlocks.push(fieldResult);
        } else if (rule.severity === 'warning') {
          mockWarnings.push(fieldResult);
        }
      }
    });
    
    setValidationResults(mockResults);
    setHardBlocks(mockHardBlocks);
    setWarnings(mockWarnings);
    
    handleNext();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Document Validation
      </Typography>
      <Typography variant="body1" paragraph>
        Upload and validate documents against predefined rules. Identify missing or invalid information.
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
          <Box component="form" onSubmit={handleSubmit(onSubmitValidationConfig)}>
            <Typography variant="h6" gutterBottom>
              Configure Validation
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Document Information
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <DocumentIcon sx={{ mr: 1 }} />
                      <Typography variant="body1">
                        {uploadedDocument?.file_path.split('/').pop() || 'Document'}
                      </Typography>
                    </Box>
                    
                    <input 
                      type="hidden" 
                      {...register('document_id')}
                      value={uploadedDocument?.document_id}
                    />
                    
                    <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                      Document Type
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {Object.keys(validationRules).map((type) => (
                        <Chip
                          key={type}
                          label={type.replace('_', ' ')}
                          onClick={() => setValue('document_type', type)}
                          color={register('document_type').value === type ? 'primary' : 'default'}
                          sx={{ textTransform: 'capitalize' }}
                        />
                      ))}
                    </Box>
                    {errors.document_type && (
                      <Typography color="error" variant="caption">
                        {errors.document_type.message}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Validation Rules
                    </Typography>
                    
                    <List dense>
                      {validationRules[register('document_type').value]?.map((rule, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            {rule.severity === 'error' ? (
                              <ErrorIcon color="error" />
                            ) : (
                              <WarningIcon color="warning" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={`${rule.field.replace('_', ' ')}`}
                            secondary={`Rule: ${rule.rule} (${rule.severity})`}
                            primaryTypographyProps={{ sx: { textTransform: 'capitalize' } }}
                          />
                        </ListItem>
                      ))}
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
                type="submit"
              >
                Validate Document
              </Button>
            </Box>
          </Box>
        )}
        
        {activeStep === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Validation Results
            </Typography>
            
            {hardBlocks.length > 0 && (
              <Alert 
                severity="error" 
                sx={{ mb: 3 }}
                action={
                  <Button color="inherit" size="small">
                    View Details
                  </Button>
                }
              >
                Document validation failed with {hardBlocks.length} critical issues
              </Alert>
            )}
            
            {hardBlocks.length === 0 && warnings.length > 0 && (
              <Alert 
                severity="warning" 
                sx={{ mb: 3 }}
                action={
                  <Button color="inherit" size="small">
                    View Details
                  </Button>
                }
              >
                Document validated with {warnings.length} warnings
              </Alert>
            )}
            
            {hardBlocks.length === 0 && warnings.length === 0 && (
              <Alert severity="success" sx={{ mb: 3 }}>
                Document validated successfully
              </Alert>
            )}
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Document Summary
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ mr: 1, fontWeight: 'bold' }}>
                        Document Type:
                      </Typography>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {validationResults?.document_type.replace('_', ' ')}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ mr: 1, fontWeight: 'bold' }}>
                        Document ID:
                      </Typography>
                      <Typography variant="body2">
                        {validationResults?.document_id}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ mr: 1, fontWeight: 'bold' }}>
                        Validation Status:
                      </Typography>
                      <Chip 
                        size="small"
                        label={hardBlocks.length === 0 ? "PASSED" : "FAILED"}
                        color={hardBlocks.length === 0 ? "success" : "error"}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Validation Statistics
                    </Typography>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-around', mb: 2 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="error.main">
                          {hardBlocks.length}
                        </Typography>
                        <Typography variant="body2">Hard Blocks</Typography>
                      </Box>
                      
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {warnings.length}
                        </Typography>
                        <Typography variant="body2">Warnings</Typography>
                      </Box>
                      
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          {validationResults?.fields.filter(f => f.passed).length || 0}
                        </Typography>
                        <Typography variant="body2">Passed</Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
              Validation Details
            </Typography>
            
            <List>
              {validationResults?.fields.map((field, index) => (
                <ListItem key={index} divider={index < validationResults.fields.length - 1}>
                  <ListItemIcon>
                    {field.passed ? (
                      <ValidIcon color="success" />
                    ) : field.severity === 'error' ? (
                      <ErrorIcon color="error" />
                    ) : (
                      <WarningIcon color="warning" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={field.field.replace('_', ' ')}
                    secondary={field.message}
                    primaryTypographyProps={{ sx: { textTransform: 'capitalize' } }}
                  />
                  <Chip 
                    size="small"
                    label={`${Math.round(field.confidence * 100)}%`}
                    color={field.passed ? "success" : "default"}
                  />
                </ListItem>
              ))}
            </List>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
              <Button onClick={handleReset} sx={{ mr: 1 }}>
                Validate Another Document
              </Button>
              <Button
                variant="contained"
                color="primary"
                disabled={hardBlocks.length > 0}
              >
                {hardBlocks.length > 0 ? 'Document Blocked' : 'Accept Document'}
              </Button>
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
}

export default DocumentValidation;
