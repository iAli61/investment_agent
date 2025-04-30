import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DescriptionIcon from '@mui/icons-material/Description';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import FilePresent from '@mui/icons-material/FilePresent';

const DocumentUpload = () => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileInput = (e) => {
    if (e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setFiles([...files, ...newFiles]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files);
      setFiles([...files, ...newFiles]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleRemoveFile = (indexToRemove) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

  const handleUpload = () => {
    // In a real implementation, this would upload files to your backend
    console.log('Uploading files:', files);
    // After successful upload, you might want to clear the files list
    // setFiles([]);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <UploadFileIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Document Analysis</Typography>
      </Box>

      <Paper
        elevation={0}
        sx={{
          p: 3,
          borderRadius: 2,
          backgroundColor: 'background.paper',
          border: '1px dashed',
          borderColor: isDragging ? 'primary.main' : 'divider',
          textAlign: 'center',
          transition: 'border-color 0.3s',
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 3,
          }}
        >
          <CloudUploadIcon
            sx={{
              fontSize: 48,
              color: isDragging ? 'primary.main' : 'text.secondary',
              mb: 2,
            }}
          />
          <Typography variant="h6" gutterBottom>
            Drop financial documents here or click to upload
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Support for PDF, Excel, CSV files
          </Typography>
          <input
            type="file"
            multiple
            onChange={handleFileInput}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={<UploadFileIcon />}
              sx={{ mt: 2 }}
            >
              Upload Documents
            </Button>
          </label>
        </Box>

        {files.length > 0 && (
          <Box sx={{ mt: 3, textAlign: 'left' }}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              Selected Files ({files.length})
            </Typography>
            <List>
              {files.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleRemoveFile(index)}
                    >
                      <DeleteOutlineIcon />
                    </IconButton>
                  }
                >
                  <ListItemIcon>
                    <FilePresent />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={`${(file.size / 1024).toFixed(2)} KB`}
                  />
                </ListItem>
              ))}
            </List>
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={files.length === 0}
              sx={{ mt: 2 }}
            >
              Upload {files.length} {files.length === 1 ? 'file' : 'files'}
            </Button>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default DocumentUpload;