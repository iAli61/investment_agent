import React, { createContext, useContext, useState } from 'react';

const FormFlowContext = createContext();

export const FormFlowProvider = ({ children }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [values, setValues] = useState({});

  const setFieldValue = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const goToNextStep = () => {
    setCurrentStep(prev => prev + 1);
  };

  return (
    <FormFlowContext.Provider value={{ currentStep, values, setFieldValue, goToNextStep }}>
      {children}
    </FormFlowContext.Provider>
  );
};

export const useFormFlow = () => {
  const context = useContext(FormFlowContext);
  if (!context) {
    throw new Error('useFormFlow must be used within a FormFlowProvider');
  }
  return context;
};

export default FormFlowContext;