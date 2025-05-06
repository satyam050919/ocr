import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  CircularProgress,
  Alert,
  Stack,
  Chip
} from '@mui/material';
import { 
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as SuccessIcon
} from '@mui/icons-material';
import { z } from 'zod';

const fileSchema = z.object({
  file: z.instanceof(File)
    .refine(file => file.size <= 10 * 1024 * 1024, {
      message: 'File size must be less than 10MB',
    })
    .refine(file => {
      const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'];
      return validTypes.includes(file.type);
    }, {
      message: 'File must be PDF, JPEG, PNG, or TIFF',
    }),
});

function DocumentUpload({ onUploadComplete, documentType }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const onDrop = React.useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      
      try {
        fileSchema.parse({ file: selectedFile });
        
        setError(null);
        setFile(selectedFile);
      } catch (err) {
        if (err.errors && err.errors.length > 0) {
          setError(err.errors[0].message);
        } else {
          setError('Invalid file. Please try again.');
        }
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif']
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (documentType) {
        formData.append('document_type', documentType);
      }
      
      
      
      
      const data = {
        document_id: `doc-${Date.now()}`,
        file_path: URL.createObjectURL(file),
        status: 'uploaded'
      };
      
      setSuccess(true);
      if (onUploadComplete) {
        onUploadComplete(data);
      }
      
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const resetUpload = () => {
    setFile(null);
    setError(null);
    setSuccess(false);
  };

  return (
    <Box sx={{ mb: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success ? (
        <Paper
          sx={{
            p: 3,
            textAlign: 'center',
            backgroundColor: 'success.light',
            color: 'success.contrastText',
          }}
        >
          <SuccessIcon fontSize="large" />
          <Typography variant="h6" sx={{ mt: 1 }}>
            Document Uploaded Successfully
          </Typography>
          <Button
            variant="contained"
            color="primary"
            sx={{ mt: 2 }}
            onClick={resetUpload}
          >
            Upload Another Document
          </Button>
        </Paper>
      ) : (
        <Paper
          {...getRootProps()}
          sx={{
            p: 3,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'divider',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
          }}
        >
          <input {...getInputProps()} />
          
          {file ? (
            <Box>
              <FileIcon color="primary" sx={{ fontSize: 48, mb: 1 }} />
              <Typography variant="subtitle1" gutterBottom>
                {file.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {(file.size / 1024).toFixed(2)} KB
              </Typography>
              
              <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUpload();
                  }}
                  disabled={uploading}
                  startIcon={uploading ? <CircularProgress size={20} /> : null}
                >
                  {uploading ? 'Uploading...' : 'Process Document'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={(e) => {
                    e.stopPropagation();
                    resetUpload();
                  }}
                  disabled={uploading}
                >
                  Cancel
                </Button>
              </Stack>
            </Box>
          ) : (
            <Box>
              <UploadIcon color="primary" sx={{ fontSize: 48, mb: 1 }} />
              <Typography variant="h6" gutterBottom>
                Drag &amp; Drop Document
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                or click to browse files
              </Typography>
              
              <Stack direction="row" spacing={1} justifyContent="center" sx={{ mt: 2 }}>
                <Chip label="PDF" size="small" />
                <Chip label="JPEG" size="small" />
                <Chip label="PNG" size="small" />
                <Chip label="TIFF" size="small" />
              </Stack>
              
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Maximum file size: 10MB
              </Typography>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
}

export default DocumentUpload;
