'use client';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import styles from './styles.css';
import { Select, MenuItem, FormControl, InputLabel, Icon, Button,  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextareaAutosize } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import debounce from 'lodash/debounce';
import HomeIcon from '@mui/icons-material/Home';
import Link from 'next/link';3


const Transcription = () => {
  const [websocket, setWebsocket] = useState(null);
  const [context, setContext] = useState(null);
  const [processor, setProcessor] = useState(null);
  const [globalStream, setGlobalStream] = useState(null);
  const [clientId, setClientId] = useState(null);
  const [roomId, setRoomId] = useState(null);
  const [sendOriginal, setSendOriginal] = useState('');
  const [currentPosition, setCurrentPosition] = useState(0);
  const [webSocketStatus, setWebSocketStatus] = useState('Not Connected');
  const [detectedLanguage, setDetectedLanguage] = useState('Undefined');
  const [processingTime, setProcessingTime] = useState('Undefined');
  const [wordErrorRate, setWordErrorRate] = useState('0%');
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [selectedAsrModel, setSelectedAsrModel] = useState('bhashini');
  const [transcription, setTranscription] = useState('');
  const [editableTranscription, setEditableTranscription] = useState('');
  const [showLoginPanel, setShowLoginPanel] = useState(true);
  const [transcriptionUrl, setTranscriptionUrl] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [openModal, setOpenModal] = useState(false);
  const [comment, setComment] = useState('');
  const websocketAddressRef = useRef(null);
  const inputSourceRef = useRef(null);
  const audioFileRef = useRef(null);
  const roomIdInputRef = useRef(null);
  const startTimeRef = useRef([0, 0, 0]);
  const endTimeRef = useRef([0, 0, 0]);

  const bufferSize = 4096;

  useEffect(() => {
    initWebSocket();
  }, []);


  useEffect(() => {
    if (sendOriginal && editableTranscription) {
      getWordErrorRate();
    }
  }, [sendOriginal, editableTranscription]);

  const initWebSocket = (offset = 'config') => {
  const websocketAddress = process.env.NEXT_PUBLIC_WEBSOCKET_URL;

    if (!websocketAddress) {
      console.log('WebSocket address is required.');
      return;
    }

    const ws = new WebSocket(websocketAddress);

    ws.onopen = () => {
      console.log('WebSocket connection established');
      setWebSocketStatus('Connected');
       


    };

    ws.onclose = (event) => {
      console.log('WebSocket connection closed', event);
      setWebSocketStatus('Not Connected');
      

    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);
      if (
        data.type === 'joined_room' ||
        data.type === 'refresh_transcription'
      ) {
        handleRoomJoined(data);
      } else {
        updateTranscription(data);
      }
    };

    setWebsocket(ws);
  };

  const handleRoomJoined = (data) => {
    setClientId(data.client_id);
    setRoomId(data.room_id);
    setTranscriptionUrl(data.transcript_url);
    setAudioUrl(data.audio_url);
    if (data.type === 'joined_room') {
      setShowLoginPanel(false);
    }
  };

  const updateTranscription = (transcriptData) => {
    if (transcriptData.words && transcriptData.words.length > 0) {
      const newTranscription = transcriptData.words
        .map((wordData) => {
          const probability = wordData.probability;
          let color = 'black';
          if (probability > 0.9) color = 'green';
          else if (probability > 0.6) color = 'orange';
          else color = 'red';
          return `<span style="color: ${color}">${wordData.word} </span>`;
        })
        .join('');
      setTranscription((prev) => prev + newTranscription + ' ');
    } else {
      setTranscription((prev) => prev + transcriptData.text + ' ');
    }
    setEditableTranscription((prev) => prev + transcriptData.text + ' ');
    setSendOriginal((prev) => prev + transcriptData.text + ' ');

    if (transcriptData.language && transcriptData.language_probability) {
      setDetectedLanguage(
        `${
          transcriptData.language
        } (${transcriptData.language_probability.toFixed(2)})`
      );
    }

    if (transcriptData.processing_time) {
      setProcessingTime(
        `Processing time: ${transcriptData.processing_time.toFixed(2)} seconds`
      );
    }
  };

  const startRecording = () => {
    if (isRecording) return;

    setIsRecording(true);

    const inputSource = document.querySelector(
      'input[name="inputSource"]:checked'
    ).value;

    if (inputSource === 'mic') {
      startMicRecording();
    } else {
      startFileRecording();
    }
  };

  const startMicRecording = () => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const newContext = new AudioContext();
    setContext(newContext);

    sendAudioConfig(newContext);
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        setGlobalStream(stream);
        const input = newContext.createMediaStreamSource(stream);
        const newProcessor = newContext.createScriptProcessor(bufferSize, 1, 1);
        newProcessor.onaudioprocess = (e) => processAudio(e, newContext);
        input.connect(newProcessor);
        newProcessor.connect(newContext.destination);
        setProcessor(newProcessor);

      })
      .catch((error) => console.error('Error accessing microphone', error));
  };

  const startFileRecording = () => {
    const file = audioFileRef.current.files[0];
    if (!file) {
      console.error('No file selected');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const arrayBuffer = reader.result;
      createAudioPipeline(arrayBuffer);
    };
    reader.readAsArrayBuffer(file);
  };


  const createAudioPipeline = (arrayBuffer) => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const newContext = new AudioContext();
    setContext(newContext);

    sendAudioConfig(newContext);
    newContext.decodeAudioData(
      arrayBuffer,
      (audioBuffer) => {
        const source = newContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(newContext.destination);

        const newProcessor = newContext.createScriptProcessor(bufferSize, 1, 1);
        newProcessor.onaudioprocess = (e) => processAudio(e, newContext);
        source.connect(newProcessor);
        newProcessor.connect(newContext.destination);

        source.start(0, currentPosition);
        setProcessor(newProcessor);
      },
      (error) => {
        console.error('Error decoding audio data:', error);
      }
    );
  };

  

 const getWordErrorRate = useCallback(() => {
    console.log(editableTranscription, sendOriginal);
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    const raw = JSON.stringify({
      "asr_transcription": sendOriginal,
      "kenlm_transcription": editableTranscription
    });

    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: raw,
      redirect: "follow"
    };

    fetch(`${process.env.NEXT_PUBLIC_WER_API}`, requestOptions)
    .then((response) => response.json())
    .then((result) => {
      const wer = (result["wer"] * 100).toFixed(2); 
      setWordErrorRate(`${wer}%`);
    })
    .catch((error) => console.error(error));
  }, [editableTranscription, sendOriginal]);

const debouncedGetWordErrorRate = useCallback(debounce(getWordErrorRate, 5000), [editableTranscription, sendOriginal]);

 useEffect(() => {
    debouncedGetWordErrorRate();
  }, [editableTranscription, sendOriginal, debouncedGetWordErrorRate]);


  const stopRecording = () => {
    if (!isRecording) return;

    setIsRecording(false);

    if (globalStream) {
      globalStream.getTracks().forEach((track) => track.stop());
      setGlobalStream(null);
    }
    if (processor) {
      setCurrentPosition(context.currentTime);
      processor.disconnect();
      setProcessor(null);
    }
    if (context) {
      context.close().then(() => setContext(null));
    }
    const now = new Date();
    endTimeRef.current = [now.getHours(), now.getMinutes(), now.getSeconds()];
  };

  const sendAudioConfig = (context) => {
    if (!context) {
      console.error('Audio context is not initialized');
      return;
    }
    const audioConfig = {
      type: 'config',
      room_id: roomId,
      client_id: clientId,
      data: {
        sampleRate: context.sampleRate,
        bufferSize: bufferSize,
        channels: 1,
        language:
          selectedLanguage !== 'multilingual'
            ? selectedLanguage
            : null,
        asr_model: selectedAsrModel,
        processing_strategy: 'silence_at_end_of_chunk',
        processing_args: {
          chunk_length_seconds: 1,
          chunk_offset_seconds: 0.1,
        },
      },
    };

    websocket.send(JSON.stringify(audioConfig));
  };

  const processAudio = (e, audioContext) => {
    if (!audioContext) {
      console.error('Audio context is not initialized');
      return;
    }
    const inputSampleRate = audioContext.sampleRate;
    const outputSampleRate = 16000;

    const left = e.inputBuffer.getChannelData(0);
    const downsampledBuffer = downsampleBuffer(
      left,
      inputSampleRate,
      outputSampleRate
    );
    const audioData = convertFloat32ToInt16(downsampledBuffer);
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const audioBase64 = bufferToBase64(audioData);
      const message = {
        type: 'audio',
        data: audioBase64,
        room_id: roomId,
        client_id: clientId,
      };
      websocket.send(JSON.stringify(message));
    }
  };

  const downsampleBuffer = (buffer, inputSampleRate, outputSampleRate) => {
    if (inputSampleRate === outputSampleRate) {
      return buffer;
    }
    const sampleRateRatio = inputSampleRate / outputSampleRate;
    const newLength = Math.round(buffer.length / sampleRateRatio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
      let accum = 0,
        count = 0;
      for (
        let i = offsetBuffer;
        i < nextOffsetBuffer && i < buffer.length;
        i++
      ) {
        accum += buffer[i];
        count++;
      }
      result[offsetResult] = accum / count;
      offsetResult++;
      offsetBuffer = nextOffsetBuffer;
    }
    return result;
  };

  const convertFloat32ToInt16 = (buffer) => {
    const l = buffer.length;
    const buf = new Int16Array(l);
    for (let i = 0; i < l; i++) {
      buf[i] = Math.min(1, buffer[i]) * 0x7fff;
    }
    return buf.buffer;
  };

  const bufferToBase64 = (buffer) => {
    const binary = String.fromCharCode.apply(null, new Uint8Array(buffer));
    return window.btoa(binary);
  };

  const createRoom = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'create_room',
        room_id: roomId,
      };
      websocket.send(JSON.stringify(message));
    }
  };

  const joinRoom = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'join_room',
        room_id: roomIdInputRef.current.value,
      };
      websocket.send(JSON.stringify(message));
    }
  };

  const updateOriginalTranscriptionServer = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const message = {
        type: 'update_transcription',
        original: sendOriginal,
        edited: editableTranscription,
        client_id: roomId,
        room_id: roomId,
        start_time: startTimeRef.current,
        end_time: endTimeRef.current,
      };
      websocket.send(JSON.stringify(message));
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
      category: 'transcription',
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
     <div className="container">
  {showLoginPanel ? (
    <div className="loginPanel">
    <div className="loginContent"> 
     <div className="headerContainer">
    <Link href="/" passHref>
      <HomeIcon fontSize="inherit" style={{ fontSize: '28px', marginLeft: '60px', marginRight: '10px', cursor: 'pointer' }} />
    </Link>
    <h1 style={{ fontSize: '28px', fontWeight: 'bold' }}>Pucar Content</h1>
  </div>

      
      <div className="formContainer">
      
        <label htmlFor="roomId">Room Id:</label>
        <input
          type="text"
          id="roomId"
          ref={roomIdInputRef}
          placeholder="Room Id"
        />
        <button
          onClick={() => {
            initWebSocket('login');
            joinRoom();
          }}
         
        >
          Join Room
        </button>
        <button
          onClick={() => {
            initWebSocket('login');
            createRoom();
          }}
           
        >
          Create Room
        </button>
      </div>
    </div>
    </div>
  ) : (
        <div className="recordingPanel">
        <div className="loginContent"> 
   <div className="headerContainer">
    <Link href="/" passHref>
      <HomeIcon  className="homeIcon" fontSize="inherit" style={{ fontSize: '28px',  marginRight: '10px', cursor: 'pointer' }} />
    </Link>
    <h1 style={{ fontSize: '28px', fontWeight: 'bold' }}>Pucar Content</h1>
  </div>
          <div className="formContainer">
           
            <h3>
              Room Id - <span>{roomId}</span>
            </h3>
            <div className="controls">
              <div className="controlGroup">
                <label htmlFor="websocketAddress">WebSocket Address:</label>
                <input
                  type="text"
                  ref={websocketAddressRef}
                  defaultValue={process.env.NEXT_PUBLIC_WEBSOCKET_URL}
                  className={`inputBox ${webSocketStatus === 'Connected' ? 'success' : webSocketStatus === 'Not Connected' ? 'error' : ''}`}
                />
              </div>
              <div className="controlGroup">
                  <FormControl fullWidth variant="outlined">
                  
                    <InputLabel id="languageSelectLabel">Language</InputLabel>
                    <Select
                      labelId="languageSelectLabel"
                      id="languageSelect"
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                      label="Language"
                      IconComponent={ExpandMoreIcon}
                    >
                     <MenuItem value="english">English</MenuItem>
                      <MenuItem value="multilingual">Multilingual</MenuItem>
                      <MenuItem value="hindi">Hindi</MenuItem>
                    </Select>
                  </FormControl>
              </div>
                <div className="controlGroup">
                  <FormControl fullWidth variant="outlined" margin="normal">
                    <InputLabel id="asrModelInput">Transcription Model</InputLabel>
                    <Select
                      labelId="asrModelInput"
                      id="asrModelSelect"
                      value={selectedAsrModel}
                      onChange={(e) => setSelectedAsrModel(e.target.value)}
                      label="Transcription  Models"
                      IconComponent={ExpandMoreIcon}
                    >
                       <MenuItem value="bhashini">Bhashini</MenuItem>
                      <MenuItem value="faster_whisper">Faster-Whisper</MenuItem>
                      <MenuItem value="whisper">Whisper</MenuItem>
                    </Select>
                  </FormControl>
                </div>

              <button onClick={() => initWebSocket()}>Connect</button>
            </div>
            <div className="inputSourceContainer">
              <label>Input Source:</label>
              <input
                type="radio"
                id="micInput"
                name="inputSource"
                value="mic"
                defaultChecked
                ref={inputSourceRef}
              />
              <label htmlFor="micInput">Microphone</label>
              <input
                type="radio"
                id="fileInput"
                name="inputSource"
                value="file"
                ref={inputSourceRef}
              />
              <label htmlFor="fileInput">File</label>
            </div>
            <input type="file" ref={audioFileRef} accept="audio/*" />
            <div className="streamingButtons">
              <button onClick={startRecording} disabled={isRecording}>Start Streaming</button>
              <button onClick={stopRecording} disabled={!isRecording}>Stop Streaming</button>
              <button onClick={updateOriginalTranscriptionServer}   disabled={isRecording || !editableTranscription.trim()} >
                Save Transcription
              </button>
            </div>

            {transcriptionUrl && audioUrl && (
              <div className="artifactDownloadPanel">
                <a
                  href={transcriptionUrl}
                  target="_blank"
                  rel="noopener noreferrer">
                  <button className="downloadButton">
                    <i className="fa fa-download"></i>
                    <span>Download Transcription</span>
                  </button>
                </a>
                <a href={audioUrl} target="_blank" rel="noopener noreferrer">
                  <button className="downloadButton" disabled={!audioUrl}>
                    <i className="fa fa-download"></i>
                    <span>Download Audio</span>
                  </button>
                </a>
              </div>
            )}

            <label htmlFor="transcription">Transcription:</label>
            <div
                id="transcription"
              className="transcription"
              dangerouslySetInnerHTML={{ __html: transcription }}></div>
          <label htmlFor="editableTranscription">Editable Transcription:</label>
            <textarea
              id= "editableTranscription"
              className="editableTranscription"
              value={editableTranscription}
              onChange={(e) => {
                    setEditableTranscription(e.target.value);
                    debouncedGetWordErrorRate();
                }
              }></textarea>
            <div>
              Word Error Rate (WER): <span>{wordErrorRate}</span>
            </div>
            <div>
              WebSocket: <span>{webSocketStatus}</span>
            </div>
            <div>
              Detected Language: <span>{detectedLanguage}</span>
            </div>
            <div>
              Last Processing Time: <span>{processingTime}</span>
            </div>
            <br></br>
             <div className="buttonContainer" style={{ display: 'flex', justifyContent: 'center' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
            
              <Button  onClick={handleFeedbackSubmit} className="submitFeedbackButton">Report Issue</Button>
              <Dialog open ={openModal} onClose={handleModalClose}>
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
        </div>
        </div>
      )}
    </div>
  );
};

export default Transcription;

