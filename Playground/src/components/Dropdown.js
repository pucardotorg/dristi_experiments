'use client';

import React from 'react';

const Dropdown = ({ options, selectedOption, onSelectOption }) => {
  return (
    <select 
        value={selectedOption} 
        onChange={(e) => onSelectOption(e.target.value)}
        style={{
            margin: '10px',
            padding: '5px',
            border: '1px solid black',
            borderRadius: '5px',
            width: '130px'
        }}    
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
};

export default Dropdown;
