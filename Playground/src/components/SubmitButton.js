'use client';

import React from 'react';

const SubmitButton = ({ onSubmit }) => {
  return (
    <button 
      onClick={onSubmit}
      className='submitBtn Btn' 
    >Submit</button>
  )
};

export default SubmitButton;
