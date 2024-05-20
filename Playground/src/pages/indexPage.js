"use client"

import React, { useState, useEffect } from "react"
import {
  Typography,
  Container,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
} from "@mui/material"

import { makeStyles } from "@material-ui/core"

const useStyles = makeStyles((theme) => ({
  container: {
    maxWidth: "100%",
    padding: theme.spacing(2),
    backgroundColor: "#ffff",
    boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
    borderRadius: 15,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  uploadedImage: {
    maxWidth: "100%",
    maxHeight: 300,
    marginTop: theme.spacing(2),
  },
  fileInputLabelContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    marginTop: theme.spacing(2),
  },
  fileInputLabel: {
    fontSize: 12,
    cursor: "pointer",
    padding: theme.spacing(1.5, 2),
    borderRadius: 5,
    textAlign: "center",
    marginBottom: theme.spacing(1),
  },

  result: {
    marginTop: theme.spacing(2),
    textAlign: "center",
  },
  submitButton: {
    marginTop: theme.spacing(2),
    borderRadius: 5,
    padding: theme.spacing(1, 2),
    fontSize: 12,
  },
  inputLabelHover: {
    "&:hover": {
      color: "#1976d2",
      cursor: "pointer",
    },
  },
  goBackBtn: {
    padding: theme.spacing(1.5, 3),
    marginTop: theme.spacing(1),
    fontSize: 12,
    borderRadius: 5,
    backgroundColor: "#f44336",
    color: "#fff",
    cursor: "pointer",
    "&:hover": {
      backgroundColor: "#d32f2f",
    },
  },
  submitFeedbackButton: {
    padding: theme.spacing(1.5, 3),
    marginTop: theme.spacing(1),
    fontSize: 12,
    borderRadius: 5,
    backgroundColor: "#1976d2",
    color: "#fff",
    cursor: "pointer",
    "&:hover": {
      backgroundColor: "#115293",
    },
  },
}))

const options = [
  { label: "Pan Card", value: "pan" },
  { label: "Cheque Return Memo", value: "cheque" },
]

const exampleTexts = {
  pan: "income, tax, department, income tax department",
  cheque: "return memo",
}

export default function IndexPage() {
  const classes = useStyles()
  const [selectedOption, setSelectedOption] = useState(options[0].value)
  const [showData, setShowData] = useState(false)
  const [jsonData, setJsonData] = useState(null)
  const [inputValues, setInputValues] = useState(options[0].value)
  const [uploadedImage, setUploadedImage] = useState(null)
  const [imageUrl, setImageUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    setIsMobile(
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      )
    )
    setInputValues(selectedOption)
  }, [selectedOption])

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value)
    setInputValues(event.target.value)
  }

  const handleInputChange = (event) => {
    setInputValues(event.target.value)
  }

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setUploadedImage(file)
      setImageUrl(url)
      setShowData(false)
      setJsonData(null)
    }
  }

  const handleSubmit = () => {
    setLoading(true)

    const valuesArray = inputValues.split(",").map((value) => value.trim())

    if (uploadedImage) {
      const formData = new FormData()
      formData.append("file", uploadedImage)
      formData.append(
        "word_check_list",
        JSON.stringify([...valuesArray, selectedOption])
      )
      formData.append("fuzz_match", false)
      formData.append("match_case", false)
      formData.append("distance_cutoff", 1)

      fetch(
        `https://ai-tools.dev.bhasai.samagra.io/ocr/pytesseract_word_check/`,
        {
          method: "POST",
          body: formData,
        }
      )
        .then((response) => response.json())
        .then((data) => {
          setJsonData(data)
          setShowData(true)
          setLoading(false)
        })
        .catch((error) => {
          console.error("Error submitting photo:", error)
          setLoading(false)
        })
    }
  }

  const handleGoBack = () => {
    setSelectedOption(options[0].value)
    setShowData(false)
    setJsonData(null)
    setInputValues(options[0].value)
    setUploadedImage(null)
    setImageUrl(null)
    setLoading(false)

    const fileInput = document.getElementById("file-input")
    if (fileInput) {
      fileInput.value = null
    }
  }

  const handleFeedbackSubmit = () => {
    console.log("Feedback submitted")
  }

  return (
    <Container className={classes.container}>
      <div className={classes.form}>
        <Typography variant="h5">Document Type Validation</Typography>
        <br></br>
        <FormControl fullWidth>
          <InputLabel
            id="option-select-label"
            className={classes.inputLabelHover}
          ></InputLabel>
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
        <TextField
          variant="outlined"
          fullWidth
          value={inputValues}
          onChange={handleInputChange}
          placeholder="Enter comma-separated values"
          style={{ marginTop: "10px" }}
        />
        <Typography
          variant="body2"
          style={{ marginTop: "10px", textAlign: "left" }}
        >
          Examples: {exampleTexts[selectedOption]}
        </Typography>
        <Box mt={2} />
        {!showData && isMobile && (
          <div className={classes.fileInputLabelContainer}>
            <Button
              variant="contained"
              component="label"
              className={classes.fileInputLabel}
            >
              Capture an image
              <input
                id="capture-input"
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleImageUpload}
                style={{ display: "none" }}
              />
            </Button>
            <Button
              variant="contained"
              component="label"
              className={classes.fileInputLabel}
            >
              Choose from device
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                style={{ display: "none" }}
              />
            </Button>
          </div>
        )}
        {!showData && !isMobile && (
          <Button
            variant="contained"
            component="label"
            className={classes.fileInputLabel}
          >
            Choose a file
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ display: "none" }}
            />
          </Button>
        )}
        {imageUrl && (
          <Typography variant="subtitle1">Selected Image</Typography>
        )}
        {imageUrl && (
          <img
            src={imageUrl}
            alt="Uploaded"
            className={classes.uploadedImage}
          />
        )}
        {!showData && uploadedImage && !loading ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            className={classes.submitButton}
          >
            Submit
          </Button>
        ) : null}
        {loading && <Typography>Loading...</Typography>}
      </div>
      {showData && jsonData && (
        <div className={classes.result}>
          <Typography variant="h5">Result</Typography>
          <pre>{JSON.stringify(jsonData, null, 2)}</pre>
          <div className={classes.buttonContainer}>
            <Button
              variant="contained"
              color="secondary"
              onClick={handleGoBack}
              className={classes.goBackBtn}
            >
              Reset
            </Button>{" "}
            <br></br>
            <Button
              variant="contained"
              onClick={handleFeedbackSubmit}
              className={classes.submitFeedbackButton}
            >
              Submit Feedback
            </Button>
          </div>
        </div>
      )}
    </Container>
  )
}
