// Work in Progress

'use client'
import React, { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {
  Container,
  Typography,
  TextField,
  Button,
  FormControl,
  RadioGroup,
  Radio,
  FormControlLabel,
  Input,
  InputLabel,
  Select,
  MenuItem,
} from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    background: '#f4f4f4',
    padding: theme.spacing(2),
  },
  controls: {
    margin: theme.spacing(2, 0),
    width: '80%',
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  controlGroup: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  label: {
    fontSize: '0.9em',
    color: '#555',
    marginBottom: theme.spacing(1),
  },
  transcriptionPanel: {
    margin: theme.spacing(2, 0),
    border: '1px solid #ddd',
    padding: theme.spacing(2),
    width: '80%',
    height: '150px',
    overflowY: 'auto',
    background: 'white',
  },
  textArea: {
    flex: 1,
    height: '180px',
    width: '81%',
    padding: theme.spacing(1),
    boxSizing: 'border-box',
  },
  button: {
    marginTop: theme.spacing(2),
    cursor: 'pointer',
  },
  artifactDownloadPanel: {
    margin: theme.spacing(3, 0),
  },
  downloadButton: {
    margin: theme.spacing(1),
  },
  formContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '300px',
    padding: theme.spacing(2),
    backgroundColor: 'white',
    boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
    borderRadius: '8px',
    marginBottom: theme.spacing(2),
  },
}));

const TranscriptionPOC = () => {
  const classes = useStyles();

  const [webSocketAddress, setWebSocketAddress] = useState('ws://localhost:8765');
  const [language, setLanguage] = useState('multilingual');
  const [inputSource, setInputSource] = useState('mic');
  const [roomID, setRoomID] = useState('');
  const [audioFile, setAudioFile] = useState(null);
  const [loggedIn, setLoggedIn] = useState(false); // State to manage login status

  const handleWebSocketAddressChange = (event) => {
    setWebSocketAddress(event.target.value);
  };

  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  const handleInputSourceChange = (event) => {
    setInputSource(event.target.value);
  };

  const handleRoomIDChange = (event) => {
    setRoomID(event.target.value);
  };

  const handleFileInputChange = (event) => {
    const file = event.target.files[0];
    setAudioFile(file);
  };

  const handleLogin = () => {
    
    setLoggedIn(true);
    
    initWebSocket();
  };

  const handleLogout = () => {
     
    setLoggedIn(false);
     
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.close();
    }
  };

  const initWebSocket = () => {
    
    const selectedLanguage = language !== 'multilingual' ? language : null;
    const audioSource = inputSource === 'file' ? 'file' : 'mic';

    const wsAddress = loggedIn ? webSocketAddress : document.getElementById('websocketAddress-login').value;

    if (!wsAddress) {
      console.log("WebSocket address is required.");
      return;
    }

    websocket = new WebSocket(wsAddress);
    websocket.onopen = () => {
      console.log("WebSocket connection established");
      document.getElementById("webSocketStatus").textContent = 'Connected';
       
    };
    websocket.onclose = event => {
      console.log("WebSocket connection closed", event);
      document.getElementById("webSocketStatus").textContent = 'Not Connected';
    
    };
    websocket.onmessage = event => {
      const data = JSON.parse(event.data);
      console.log(data);
       
      if (data.type === 'joined_room' || data.type === 'refresh_transcription') {
        
        setRoomID(data.room_id);  
      } else {
      
        updateTranscription(data);
      }
    };
  };

  const joinRoom = () => {
    const room_id = document.getElementById('room-id').value;
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'join_room',
        room_id: room_id,
      };
      websocket.send(JSON.stringify(message));
    }
  };
   const startRecording = () => {
   
    console.log('Starting recording...');
  };
const stopRecording = () => {
    
    console.log('Starting recording...');
  };
const save_text = () => {
    
    console.log('Starting recording...');
  };

  const createRoom = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'create_room',
        room_id: roomID,
      };
      websocket.send(JSON.stringify(message));
    }
  };

  const updateTranscription = (transcript_data) => {
   
    console.log('Updating transcription:', transcript_data);
   
  };

  return (
    <Container className={classes.root}>
      {!loggedIn && (  
        <div id="login-panel" className={classes.formContainer}>
          <Typography variant="h3">Pucar Login</Typography>
          <InputLabel className={classes.label} htmlFor="websocketAddress-login">WebSocket Address:</InputLabel>
          <Input
            id="websocketAddress-login"
            type="text"
            value={webSocketAddress}
            onChange={handleWebSocketAddressChange}
          />
          <InputLabel className={classes.label} htmlFor="room-id">Room Id:</InputLabel>
          <Input
            id="room-id"
            type="text"
            value={roomID}
            onChange={handleRoomIDChange}
          />
          <div className={classes.controls}>
            <Button variant="contained" color="primary" onClick={handleLogin} className={classes.button}>
              Connect
            </Button>
            <Button variant="contained" color="primary" onClick={joinRoom} className={classes.button}>
              Join Room
            </Button>
            <Button variant="contained" color="primary" onClick={createRoom} className={classes.button}>
              Create Room
            </Button>
          </div>
        </div>
      )}

      {loggedIn && (  
        <>
          <Typography variant="h1">Transcription POC</Typography>
          <Typography variant="h3">Room Id - <span id="meet-id">{roomID}</span></Typography>

          <div className={classes.controls}>
            <div className={classes.controlGroup}>
              <InputLabel className={classes.label} htmlFor="websocketAddress">WebSocket Address:</InputLabel>
              <Input
                id="websocketAddress"
                type="text"
                value={webSocketAddress}
                onChange={handleWebSocketAddressChange}
              />
            </div>

            <div className={classes.controlGroup}>
              <InputLabel className={classes.label} htmlFor="languageSelect">Language:</InputLabel>
              <Select
                id="languageSelect"
                value={language}
                onChange={handleLanguageChange}
              >
                <MenuItem value="multilingual">Multilingual</MenuItem>
                <MenuItem value="english">English</MenuItem>
                <MenuItem value="hindi">Hindi</MenuItem>
              </Select>
            </div>

            <div className={classes.controlGroup}>
              <FormControl component="fieldset">
                <InputLabel className={classes.label}>Input Source:</InputLabel>
                <RadioGroup row aria-label="inputSource" name="inputSource" value={inputSource} onChange={handleInputSourceChange}>
                  <FormControlLabel value="mic" control={<Radio />} label="Microphone" />
                  <FormControlLabel value="file" control={<Radio />} label="File" />
                </RadioGroup>
              </FormControl>
            </div>

            {inputSource === 'file' && (
              <div className={classes.controlGroup}>
                <input
                  accept="audio/*"
                  style={{ display: 'none' }}
                  id="audio_file"
                  type="file"
                  onChange={handleFileInputChange}
                />
                <label htmlFor="audio_file">
                  <Button variant="contained" component="span" className={classes.button}>
                    Select Audio File
                  </Button>
                </label>
              </div>
            )}

            <Button variant="contained" color="primary" onClick={initWebSocket} className={classes.button}>
              Connect
            </Button>

            <Button variant="contained" color="secondary" onClick={handleLogout} className={classes.button}>
              Logout
            </Button>
          </div>

          <div id="transcription" className={classes.transcriptionPanel}>
           
            </div>

            <textarea
              id="editable-transcription"
              className={classes.textArea}
              placeholder="Editable Transcription"
              rows={5}
            />

            <div className={classes.controls}>
              <Button
                id="startButton"
                variant="contained"
                color="primary"
                onClick={startRecording}
                className={classes.button}
              >
                Start Recording
              </Button>

              <Button
                id="stopButton"
                variant="contained"
                color="secondary"
                onClick={stopRecording}
                className={classes.button}
              >
                Stop Recording
              </Button>

              <Button
                id="save_the_transcription"
                variant="contained"
                color="primary"
                onClick={save_text}
                className={classes.button}
              >
                Save Transcription
              </Button>
            </div>

            <div id="artifact-download-panel" className={classes.artifactDownloadPanel}>
              <Button
                id="trans-download-link"
                variant="contained"
                color="primary"
                className={classes.downloadButton}
                href=""
                target="_blank"
                rel="noopener noreferrer"
              >
                Download Transcription
              </Button>
              <Button
                id="audio-download-link"
                variant="contained"
                color="primary"
                className={classes.downloadButton}
                href=""
                target="_blank"
                rel="noopener noreferrer"
              >
                Download Audio
              </Button>
            </div>
          </>
        )}
      </Container>
    );
  };

  export default TranscriptionPOC;
