import React from 'react';
import { Box, Grid, TextField, MenuItem, Button } from '@mui/material';

const DynamicForm = ({ fields, values, onChange, onSubmit, isSubmitting }) => (
  <Box component="form" onSubmit={onSubmit}>
    <Grid container spacing={2}>
      {fields.map(field => (
        <Grid item xs={12} md={field.gridMd || 6} key={field.name}>
          {field.type === 'select' ? (
            <TextField
              select
              fullWidth
              label={field.label}
              name={field.name}
              value={values[field.name] || ''}
              onChange={onChange}
              variant="outlined"
              required={field.required}
            >
              {field.options.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>
          ) : (
            <TextField
              fullWidth
              label={field.label}
              name={field.name}
              type={field.type}
              value={values[field.name] || ''}
              onChange={onChange}
              variant="outlined"
              required={field.required}
            />
          )}
        </Grid>
      ))}
    </Grid>
    <Box sx={{ mt: 3, textAlign: 'right' }}>
      <Button type="submit" variant="contained" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Next'}
      </Button>
    </Box>
  </Box>
);

export default DynamicForm;
