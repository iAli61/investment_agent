import React, { useState } from 'react';
import { Container, Typography, Box, Paper } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import DynamicForm from '../components/common/DynamicForm';

/**
 * NewAnalysis page - step-by-step guided form
 */
const NewAnalysis = () => {
  // Property type options for select step
  const propertyTypeOptions = [
    { value: 'apartment', label: 'Apartment' },
    { value: 'house', label: 'House' },
    { value: 'multi-family', label: 'Multi-Family Home' },
    { value: 'commercial', label: 'Commercial Property' },
  ];

  // Define form steps
  const steps = [
    {
      title: 'Enter Property Address',
      fields: [
        { name: 'address', label: 'Property Address', type: 'text', required: true, gridMd: 12 },
      ],
    },
    {
      title: 'Property Details',
      fields: [
        { name: 'askingPrice', label: 'Asking Price (€)', type: 'number', required: true },
        { name: 'propertyType', label: 'Property Type', type: 'select', required: true, options: propertyTypeOptions },
      ],
    },
  ];

  const [currentStep, setCurrentStep] = useState(0);
  const [values, setValues] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    // advance to next step or trigger analysis at final step
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
      setIsSubmitting(false);
    } else {
      // TODO: call backend to start analysis with collected values
      console.log('Starting analysis with:', values);
      setIsSubmitting(false);
      alert(`Starting analysis for: ${values.address}, price ${values.askingPrice}, type ${values.propertyType}`);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        {steps[currentStep].title}
      </Typography>
      <Paper elevation={0} sx={{ p: 4, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
        <DynamicForm
          fields={steps[currentStep].fields}
          values={values}
          onChange={handleChange}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />
      </Paper>
    </Container>
  );
};

export default NewAnalysis;