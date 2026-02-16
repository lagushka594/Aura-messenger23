let voiceSocket = null;
let peerConnection = null;
let localStream = null;
const config = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };

function initVoiceSocket(roomId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    voiceSocket = new WebSocket(protocol + '//' + window.location.host + '/ws/voice/' + roomId + '/');

    voiceSocket.onopen = function() {
        console.log('Voice socket connected');
    };

    voiceSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        handleVoiceSignal(data);
    };

    voiceSocket.onclose = function() {
        console.log('Voice socket closed');
    };
}

function handleVoiceSignal(data) {
    if (!peerConnection) {
        createPeerConnection();
    }
    switch (data.type) {
        case 'offer':
            peerConnection.setRemoteDescription(new RTCSessionDescription(data))
                .then(() => peerConnection.createAnswer())
                .then(answer => peerConnection.setLocalDescription(answer))
                .then(() => {
                    voiceSocket.send(JSON.stringify({
                        type: 'answer',
                        sdp: peerConnection.localDescription.sdp
                    }));
                })
                .catch(error => console.error('Error handling offer:', error));
            break;
        case 'answer':
            peerConnection.setRemoteDescription(new RTCSessionDescription(data))
                .catch(error => console.error('Error setting remote description:', error));
            break;
        case 'candidate':
            if (data.candidate) {
                peerConnection.addIceCandidate(new RTCIceCandidate(data))
                    .catch(error => console.error('Error adding ICE candidate:', error));
            }
            break;
    }
}

function createPeerConnection() {
    peerConnection = new RTCPeerConnection(config);
    peerConnection.onicecandidate = (event) => {
        if (event.candidate && voiceSocket && voiceSocket.readyState === WebSocket.OPEN) {
            voiceSocket.send(JSON.stringify({
                type: 'candidate',
                candidate: event.candidate.candidate,
                sdpMid: event.candidate.sdpMid,
                sdpMLineIndex: event.candidate.sdpMLineIndex
            }));
        }
    };
    peerConnection.ontrack = (event) => {
        const audio = document.createElement('audio');
        audio.srcObject = event.streams[0];
        audio.autoplay = true;
        audio.controls = true;
        document.body.appendChild(audio);
        console.log('Remote track received');
    };
}

async function startAudio() {
    if (!voiceSocket || voiceSocket.readyState !== WebSocket.OPEN) {
        console.error('Voice socket not open');
        alert('Соединение с голосовым каналом не установлено');
        return;
    }
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        if (!peerConnection) {
            createPeerConnection();
        }
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
        document.getElementById('start-audio').disabled = true;
        document.getElementById('stop-audio').disabled = false;

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        voiceSocket.send(JSON.stringify({
            type: 'offer',
            sdp: peerConnection.localDescription.sdp
        }));
    } catch (err) {
        console.error('Error accessing microphone:', err);
        alert('Не удалось получить доступ к микрофону');
    }
}

function stopAudio() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    document.getElementById('start-audio').disabled = false;
    document.getElementById('stop-audio').disabled = true;
}

// Экспорт функций для использования в HTML
window.startAudio = startAudio;
window.stopAudio = stopAudio;

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-audio');
    const stopBtn = document.getElementById('stop-audio');
    if (startBtn) {
        startBtn.addEventListener('click', startAudio);
    }
    if (stopBtn) {
        stopBtn.addEventListener('click', stopAudio);
    }
});