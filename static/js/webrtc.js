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
    if (!peerConnection) createPeerConnection();
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
                });
            break;
        case 'answer':
            peerConnection.setRemoteDescription(new RTCSessionDescription(data));
            break;
        case 'candidate':
            peerConnection.addIceCandidate(new RTCIceCandidate(data));
            break;
    }
}

function createPeerConnection() {
    peerConnection = new RTCPeerConnection(config);
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            voiceSocket.send(JSON.stringify({
                type: 'candidate',
                candidate: event.candidate.candidate,
                sdpMid: event.candidate.sdpMid,
                sdpMLineIndex: event.candidate.sdpMLineIndex
            }));
        }
    };
    peerConnection.ontrack = (event) => {
        // Добавляем удалённый аудиопоток на страницу (можно создать скрытый элемент audio)
        const audio = document.createElement('audio');
        audio.srcObject = event.streams[0];
        audio.autoplay = true;
        audio.controls = true;
        document.body.appendChild(audio);
    };
}

document.getElementById('start-audio')?.addEventListener('click', async () => {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
        document.getElementById('start-audio').disabled = true;
        document.getElementById('stop-audio').disabled = false;

        // Создаём предложение (offer) для инициации соединения
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
});

document.getElementById('stop-audio')?.addEventListener('click', () => {
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
});