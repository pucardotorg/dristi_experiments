'use client'
import React, { useState, useEffect } from 'react';
import {
  Typography,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextareaAutosize
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HomeIcon from '@mui/icons-material/Home';
import Link from 'next/link';

import './styles.css'

const options = [
  { label: 'Cheque Return Memo', value: ['cheque','return','memo'] },
  { label: 'Legal Notice', value: ['Legal Notice', 'Demand Notice'] },
  { label: 'Vakalath', value: ['Vakalat', 'Vakalatnama'] },
];

export default function DataExtraction() {
  const [selectedOption, setSelectedOption] = useState(options[0].value);
  const [showData, setShowData] = useState(false);
  const [jsonData, setJsonData] = useState(null);
  const [inputValues, setInputValues] = useState(options[0].value);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [comment, setComment] = useState('');

  useEffect(() => {
    setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
    setInputValues(selectedOption);
  }, [selectedOption]);

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value);
    setInputValues(event.target.value);
  };

  const handleInputChange = (event) => {
    setInputValues(event.target.value);
  };

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setUploadedImage(file);
      setImageUrl(url);
      setShowData(false);
      setJsonData(null);
    }
  };

  const handleSubmit = () => {
    setLoading(true);

    const valuesString = Array.isArray(inputValues) ? inputValues.join(',') : inputValues;
    const valuesArray = valuesString ? valuesString.split(',').map(value => value.trim()) : [];

    if (uploadedImage) {
      const formData = new FormData();
      formData.append('file', uploadedImage);
      formData.append('word_check_list', JSON.stringify(valuesArray));
      formData.append('distance_cutoff', 1);
      formData.append('doc_type', 'cheque_return_memo');
      formData.append('extract_data', 'true');

      fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}`, {
        method: 'POST',
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          setJsonData(data);
          setShowData(true);
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error submitting photo:', error);
          setLoading(false);
          alert('Failed to submit the photo. Please try again');
        });
    }
  };

  const handleGoBack = () => {
    setSelectedOption(options[0].value);
    setShowData(false);
    setJsonData(null);
    setInputValues(options[0].value);
    setUploadedImage(null);
    setImageUrl(null);
    setLoading(false);

    const fileInput = document.getElementById('file-input');
    if (fileInput) {
      fileInput.value = null;
    }
  };

  const handleFeedbackSubmit = () => {
    setOpenModal(true);
  };

  const handleModalClose = () => {
    setOpenModal(false);
    setComment('');
  };

  const handleCommentChange = (event) => {
    setComment(event.target.value);
  };

  const handleCommentSubmit = () => {
    const data = {
      category: 'ocr',
      text: comment,
    };

    fetch(`${process.env.NEXT_PUBLIC_REPORT_ISSUE_API}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        handleModalClose();
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  return (
    <div>
     <Grid container alignItems="center" justifyContent="center" spacing={1}>
  <Grid item>
    <Link href="/" passHref>
      <HomeIcon fontSize="inherit" style={{ fontSize: '60px', marginRight: '10px', cursor: 'pointer' }} />
    </Link>
  </Grid>
  <Grid item>
    <Typography variant="h3" className="title">Data Extraction</Typography>
  </Grid>
</Grid>
      <div className="form">
        <Grid container alignItems="center" spacing={2}>
          <Grid item>
            <Typography variant="h6">Document Type:</Typography>
          </Grid>
          <Grid item xs>
            <FormControl fullWidth>
              <InputLabel id="option-select-label" className="inputLabelHover"></InputLabel>
              <Select
                labelId="option-select-label"
                id="option-select"
                value={selectedOption}
                onChange={handleOptionChange}
              >
                {options.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        <Grid container alignItems="center" spacing={8.5}>
          <Grid item>
            <Typography variant="h6">Keywords:</Typography>
          </Grid>
          <Grid item xs>
            <TextField
              variant="outlined"
              fullWidth
              value={inputValues}
              onChange={handleInputChange}
              placeholder="Enter comma-separated values"
              style={{ marginTop: '10px' }}
            />
          </Grid>
        </Grid>
        <Box mt={2} />
        {isMobile && (
          <div className="fileInputLabelContainer" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Button variant="contained" component="label" className="fileInputLabel" style={{ width: '150px', padding: '10px', marginBottom: '10px' }}>
              Capture an image
              <input id="capture-input" type="file" accept="image/*" capture="environment" onChange={handleImageUpload} style={{ display: 'none' }} />
            </Button>
            <Button variant="contained" component="label" className="fileInputLabel" style={{ width: '150px', padding: '10px' }}>
              <SearchIcon />
              Select File(s)
              <input id="file-input" type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} />
            </Button>
            {imageUrl && (
              <div style={{ textAlign: 'center', marginTop: '10px', maxWidth: '100%' }}>
                <img src={imageUrl} alt="Uploaded" className="uploadedImage" style={{ maxWidth: '100%', maxHeight: '300px' }} />
              </div>
            )}
          </div>
        )}
        {!isMobile && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Button variant="" component="label" className="fileInputLabel" style={{ marginRight: '10px' }}>
              <SearchIcon style={{ marginRight: '5px' }} />
              <Typography variant="body1">Select File(s)</Typography>
              <input id="file-input" type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} />
            </Button>
            {imageUrl && <img src={imageUrl} alt="Uploaded" className="uploadedImage" />}
          </div>
        )}
        {imageUrl && <Typography variant="h6"> </Typography>}
        {!showData && uploadedImage && !loading ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            className="submitButton"
            sx={{ fontSize: '20px', padding: '12px 24px', width: '100%' }}
          >
            Submit for Extraction
          </Button>
        ) : null}
        {loading && <Typography>Loading...</Typography>}
        {showData && jsonData && (
          <div className="result">
            <Grid container spacing={2}>
              <Grid item xs={4} sm={3} md={2} lg={1}>
                <Typography variant="h6" align="left">Contains Keywords:</Typography>
              </Grid>
              <Grid item xs={8} sm={9} md={10} lg={11}>
                <Typography variant="body1" align="right" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {jsonData['Contains Keywords'] && Object.entries(jsonData['Contains Keywords']).map(([key, value]) => (
                    <div key={key}>
                      <p>{key}: {value === 0 ? 'No match' : 'Match'}</p>
                    </div>
                  ))}
                </Typography>
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={4} sm={3} md={2} lg={1}>
                <Typography variant="h6" align="left">Extracted Data:</Typography>
              </Grid>
              <Grid item xs={8} sm={9} md={10} lg={11}>
                <Typography variant="body1" align="right" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {jsonData['Extracted Data'] && Object.entries(jsonData['Extracted Data']).map(([key, value]) => (
                    <div key={key}>
                      <p>{key}: {value ? value : 'Not available'}</p>
                    </div>
                  ))}
                </Typography>
              </Grid>
            </Grid>
            <div className="buttonContainer" style={{ display: 'flex', justifyContent: 'center' }}>
              <div style={{ display: 'flex', gap: '10px' }}>
                <Button variant="contained" color="secondary" onClick={handleGoBack} className="goBackBtn">Reset</Button>
                <Button variant="contained" onClick={handleFeedbackSubmit} className="submitFeedbackButton">Report Issue</Button>
                <Dialog open={openModal} onClose={handleModalClose}>
                  <DialogTitle>Feedback</DialogTitle>
                  <DialogContent>
                    <TextareaAutosize
                      minRows={4}
                      placeholder="Enter your comments here"
                      value={comment}
                      onChange={handleCommentChange}
                      style={{ width: '100%' }}
                    />
                  </DialogContent>
                  <DialogActions>
                    <Button onClick={handleModalClose} color="primary">
                      Cancel
                    </Button>
                    <Button onClick={handleCommentSubmit} color="primary">
                      Submit
                    </Button>
                  </DialogActions>
                </Dialog>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
