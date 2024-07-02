/**
 * VoiceStreamAI Client - WebSocket-based real-time transcription
 *
 * Contributor:
 * - Alessandro Saccoia - alessandro.saccoia@gmail.com
 */

let websocket;
let context;
let processor;
let globalStream;
let clientId = null; // Variable to store the client ID
let roomId = null;
let start_time = [0, 0, 0];
let end_time = [0, 0, 0];
const websocket_uri = 'ws://localhost:8765';
const bufferSize = 4096;
let isRecording = false;
let send_original = "";
let currentPosition = 0;


function renderPortal() {
    let recordingPanel = document.getElementById('recording-panel');
    let loginPanel = document.getElementById('login-panel');

    if(roomId == null && clientId == null) {
        recordingPanel.classList.add('hidden');
        loginPanel.classList.remove('hidden');
    } else {
        loginPanel.classList.add('hidden');
        recordingPanel.classList.remove('hidden');
    }
}

function initWebSocket(offset="config") {
    let websocketAddress;
    if(offset === "config") {
        websocketAddress = document.getElementById('websocketAddress').value;
    } else {
       websocketAddress = document.getElementById('websocketAddress-login').value;
    }
//    chunk_length_seconds = document.getElementById('chunk_length_seconds').value;
//    chunk_offset_seconds = document.getElementById('chunk_offset_seconds').value;
    chunk_length_seconds = 1;
    chunk_offset_seconds = 0.1;
    const selectedLanguage = document.getElementById('languageSelect').value;
    const selectedInputSource = document.querySelector('input[name="inputSource"]:checked').value;
    const fileInput = document.getElementById('audio_file');

    if (selectedInputSource === 'file') {
        fileInput.disabled = false;
    } else {
        fileInput.disabled = false;
    }

    language = selectedLanguage !== 'multilingual' ? selectedLanguage : null;
    
    if (!websocketAddress) {
        console.log("WebSocket address is required.");
        return;
    }

    websocket = new WebSocket(websocketAddress);
    websocket.onopen = () => {
        console.log("WebSocket connection established");
        document.getElementById("webSocketStatus").textContent = 'Connected';
        document.getElementById('startButton').disabled = false;
        document.getElementById('save_the_transcription').disabled = false;
        document.getElementById('audio_file').disabled = false;
    };
    websocket.onclose = event => {
        console.log("WebSocket connection closed", event);
        document.getElementById("webSocketStatus").textContent = 'Not Connected';
        document.getElementById('startButton').disabled = false;
        document.getElementById('stopButton').disabled = false;
        document.getElementById('save_the_transcription').disabled = false;
    };
    websocket.onmessage = event => {
        const data = JSON.parse(event.data);
        console.log(data);
        if (data.type === 'joined_room' || data.type === 'refresh_transcription') {
            // Handle the client ID
            artifactDownloadPanel = document.getElementById("artifact-download-panel")
            clientId = data.client_id;
            roomId = data.room_id;
            transcriptionUrl = data.transcript_url
            audioUrl = data.audio_url
            document.getElementById("meet-id").textContent = roomId;
            console.log()
            if(transcriptionUrl != "" && audioUrl != "") {
                artifactDownloadPanel.classList.remove("hidden");
                document.getElementById("trans-download-link").href = transcriptionUrl;
                document.getElementById("audio-download-link").href = audioUrl;
            } else {
                artifactDownloadPanel.classList.add("hidden");
            }
            if(data.type === 'joined_room' ) {
                renderPortal();
            }
        } else {
                // Handle other types of messages (e.g., transcription data)
            updateTranscription(data);
        }
    };
}

function updateTranscription(transcript_data) {
    const transcriptionDiv = document.getElementById('transcription');
    const languageDiv = document.getElementById('detected_language');
    const textArea = document.getElementById('editable-transcription');
    // console.log(transcript_data);   
    if (transcript_data['words'] && transcript_data['words'].length > 0) {
        // Append words with color based on their probability
        transcript_data['words'].forEach(wordData => {
            const span = document.createElement('span');
            const probability = wordData['probability'];
            span.textContent = wordData['word'] + ' ';

            // Set the color based on the probability
            if (probability > 0.9) {
                span.style.color = 'green';
            } else if (probability > 0.6) {
                span.style.color = 'orange';
            } else {
                span.style.color = 'red';
            }

            transcriptionDiv.appendChild(span);
            // textArea.value += wordData['word'] + ' ';
            console.log(span.textContent);

        });
        textArea.value += transcript_data['text'] + ' ';
        send_original += transcript_data['text'] + '\n';
        // Add a new line at the end
        transcriptionDiv.appendChild(document.createElement('br'));
    } else {
        // Fallback to plain text
        transcriptionDiv.textContent += transcript_data['text'] + ' ';
        textArea.value += transcript_data['text'] + ' ';
    }

    // Update the language information
    if (transcript_data['language'] && transcript_data['language_probability']) {
        languageDiv.textContent = transcript_data['language'] + ' (' + transcript_data['language_probability'].toFixed(2) + ')';
    }

    // Update the processing time, if available
    const processingTimeDiv = document.getElementById('processing_time');
    if (transcript_data['processing_time']) {
        processingTimeDiv.textContent = 'Processing time: ' + transcript_data['processing_time'].toFixed(2) + ' seconds';
    }
}

function save_text() {
    const edited_text = document.getElementById('editable-transcription').value;
    const orginal_text = document.getElementById('transcription').textContent;
    fetch('http://127.0.0.1:5001/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            original: send_original,
            edited: edited_text,
            client_id: roomId,
            room_id: roomId,
            start_time: start_time,
            end_time: end_time
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server response:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
    document.getElementById('save_the_transcription').disabled = false;
//    document.getElementById('editable-transcription').value = '';
//    document.getElementById('transcription').textContent = '';
}
function startRecording() {
    if (isRecording) return;
    isRecording = true;

    const inputSource = document.querySelector('input[name="inputSource"]:checked').value;

    if (inputSource === 'mic') {
        startMicRecording();
    } else {
        startFileRecording();
    }
}
function startMicRecording() {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const newContext = new AudioContext();
    setContext(newContext);

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        globalStream = stream;
        const input = context.createMediaStreamSource(stream);
        const processor = context.createScriptProcessor(bufferSize, 1, 1);
        processor.onaudioprocess = e => processAudio(e,newContext);
        input.connect(processor);
        processor.connect(context.destination);
        setProcessor(newProcessor);

        sendAudioConfig();
    }).catch(error => console.error('Error accessing microphone', error));

    // Disable start button and enable stop button
    document.getElementById('startButton').disabled = true;
    document.getElementById('stopButton').disabled = false;
}
function createAudioPipeline(arrayBuffer) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const newContext = new AudioContext();
    setContext(newContext);

    newContext.decodeAudioData(arrayBuffer, (audioBuffer) => {
        const source = newContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(newContext.destination); // Connect to the destination to play the audio

        // Create the ScriptProcessorNode and connect it to the source
        const newProcessor = newContext.createScriptProcessor(bufferSize, 1, 1);
        newProcessor.onaudioprocess = e => processAudio(e, newContext, source);
        source.connect(newProcessor);
        newProcessor.connect(newContext.destination);

        // Start playing the audio from the current position
        source.start(0, currentPosition);
        setProcessor(newProcessor);

        sendAudioConfig();
    }, (error) => {
        console.error('Error decoding audio data:', error);
    });
}
function startFileRecording() {
    const fileInput = document.getElementById('audio_file');
    const file = fileInput.files[0];

    if (!file) {
        console.error('No file selected');
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        const arrayBuffer = reader.result;
        createAudioPipeline(arrayBuffer);
        document.getElementById('startButton').disabled = true;
        document.getElementById('stopButton').disabled = false;
    };
    reader.readAsArrayBuffer(file);

}

function stopRecording() {
    if (!isRecording) return;
    isRecording = false;

    if (globalStream) {
        globalStream.getTracks().forEach(track => track.stop());
    }
    if (processor) {
        // Get the current position before disconnecting
        currentPosition = context.currentTime;
        processor.disconnect();
        processor = null;
    }
    if (context) {
        context.close().then(() => context = null);
    }
    var d = new Date();
    end_time[0] = d.getHours();
    end_time[1] = d.getMinutes();
    end_time[2] = d.getSeconds();
    document.getElementById('save_the_transcription').disabled = false;
    document.getElementById('startButton').disabled = false;
    document.getElementById('stopButton').disabled = true;
}

function sendAudioConfig() {
//    let selectedStrategy = document.getElementById('bufferingStrategySelect').value;
    let selectedStrategy = 'silence_at_end_of_chunk';
    let processingArgs = {};

    if (selectedStrategy === 'silence_at_end_of_chunk') {
        processingArgs = {
//            chunk_length_seconds: parseFloat(document.getElementById('chunk_length_seconds').value),
//            chunk_offset_seconds: parseFloat(document.getElementById('chunk_offset_seconds').value)
            chunk_length_seconds: 1,
            chunk_offset_seconds: 0.1
        };
    }

    const audioConfig = {
        type: 'config',
        room_id: roomId,
        client_id: clientId,
        data: {
            sampleRate: context.sampleRate,
            bufferSize: bufferSize,
            channels: 1, // Assuming mono channel
            language: language,
            processing_strategy: selectedStrategy, 
            processing_args: processingArgs
        }
    };

    websocket.send(JSON.stringify(audioConfig));
}

function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
    if (inputSampleRate === outputSampleRate) {
        return buffer;
    }
    var sampleRateRatio = inputSampleRate / outputSampleRate;
    var newLength = Math.round(buffer.length / sampleRateRatio);
    var result = new Float32Array(newLength);
    var offsetResult = 0;
    var offsetBuffer = 0;
    while (offsetResult < result.length) {
        var nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
        var accum = 0, count = 0;
        for (var i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
            accum += buffer[i];
            count++;
        }
        result[offsetResult] = accum / count;
        offsetResult++;
        offsetBuffer = nextOffsetBuffer;
    }
    return result;
}

function processAudio(e,context,source) {
    const inputSampleRate = context.sampleRate;
    const outputSampleRate = 16000; // Target sample rate

    const left = e.inputBuffer.getChannelData(0);
    const downsampledBuffer = downsampleBuffer(left, inputSampleRate, outputSampleRate);
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
//        websocket.send(audioData);
    }

}

function convertFloat32ToInt16(buffer) {
    let l = buffer.length;
    const buf = new Int16Array(l);
    while (l--) {
        buf[l] = Math.min(1, buffer[l]) * 0x7FFF;
    }
    return buf.buffer;
}

// Initialize WebSocket on page load
window.onload = initWebSocket();
renderPortal();

function toggleBufferingStrategyPanel() {
    var selectedStrategy = document.getElementById('bufferingStrategySelect').value;
    if (selectedStrategy === 'silence_at_end_of_chunk') {
        var panel = document.getElementById('silence_at_end_of_chunk_options_panel');
        panel.classList.remove('hidden');
    } else {
        var panel = document.getElementById('silence_at_end_of_chunk_options_panel');
        panel.classList.add('hidden');
    }
}

function createRoom() {
    console.log("createRoom");
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const message = {
            type: 'create_room',
            room_id: roomId,
        };
        websocket.send(JSON.stringify(message));
    }
}

function joinRoom() {
    const room_id = document.getElementById('room-id').value;
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const message = {
            type: 'join_room',
            room_id: room_id,
        };
        websocket.send(JSON.stringify(message));
    }
}

function updateOriginalTranscriptionServer() {
    const edited_text = document.getElementById('editable-transcription').value;
    const orginal_text = document.getElementById('transcription').textContent;
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        const message = {
            type: 'update_transcription',
            original: send_original,
            edited: edited_text,
            client_id: roomId,
            room_id: roomId,
            start_time: start_time,
            end_time: end_time
        };
        websocket.send(JSON.stringify(message));
        document.getElementById('save_the_transcription').disabled = true;
    }
}

function bufferToBase64(buffer) {
    const binary = String.fromCharCode.apply(null, new Uint8Array(buffer));
    return window.btoa(binary);
}