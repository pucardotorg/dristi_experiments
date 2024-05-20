// Depreciated may not be required

'use client';

import '@fontsource/roboto';
import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';

const Camera = ({ onCapture }) => {
  const webcamRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);

  const capture = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImageSrc(imageSrc);
    onCapture(imageSrc);
  };

  const retake = () => {
    setImageSrc(null)
    onCapture(null)
  }

  return (
    <>
      {
        imageSrc === null && (
          <>
            <Webcam 
              audio={false} 
              ref={webcamRef} 
              screenshotFormat="image/png" 
              style={{
                  width: '29vw',
                  height: '22vw',
                  borderRadius: '10px',
                  boxShadow: '0 0 10px rgb(55, 57, 57)'
              }}
            />
            <button 
              onClick={capture}
              className='capBtn Btn'
            >Capture</button>
          </>
          
        ) 
      }
      
      {
        imageSrc && <>
          <img 
            src={imageSrc} 
            alt="Captured" 
            style={{
              borderRadius: '10px',
              boxShadow: '0 0 10px rgb(55, 57, 57)'
            }}
          />
          <button
            onClick={retake}
            className='Btn reBtn'
          >
            Re-Capture
          </button>
        </> 
      }
      
    </>
  );
};

export default Camera;
