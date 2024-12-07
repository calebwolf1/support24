import io from 'socket.io-client';


function connectWebSocket(url) {
  return new Promise((resolve, reject) => {
    const sock = io(url);

    sock.on('connect', () => {
      console.log('Connected to server');
      resolve(sock);
    });

    sock.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    sock.on('chunk_received', (data) => {
      console.log('Received message from server');
    })

    sock.on('connect_error', (error) => {
      console.log('Connection failed:', error);
      reject(error);
    })
  });
};

function areAllCharactersEqual(str) {
  if (str.length <= 1) return true; // Single character or empty string is trivially true

  const firstChar = str[0];
  for (let i = 1; i < str.length; i++) {
      if (str[i] !== 'A' && str[i] !== '=') {
          return false;
      }
  }
  return true;
}

export {connectWebSocket, areAllCharactersEqual};