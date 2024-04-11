import socket
import wave
from loguru import logger
import pyaudio
import numpy as np
import time
import threading


PORT_INC = 10098
# FORMAT = pyaudio.paFloat32

# Create an instance of ProcessData() to send to server.
# variable = SocketMessage()
# # Pickle the object and send it to the server
# data_string = pickle.dumps(variable)
# s.send(b'test')

class ChunkSenderThread():
    def __init__(self):
        # super().__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('192.168.1.100', 10500))
        
    def run(self):
        while True:
            user_input = input('Enter your speech')
            
            if user_input.lower() == 'quit':
                break
            
            self.s.sendall(user_input.encode())
        logger.debug('Exiting ChunkSender')


class SpeakingThread(threading.Thread):
    def __init__(self):
        super().__init__()
        CHANNELS = 1
        RATE = 12000
        # CHUNK_SIZE = 1024

        HOST = '192.168.1.100'
        # Create a socket connection.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, 10501))
        

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=2,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)

        # output_wavfile = 'test.wav'
        # wf = wave.open(output_wavfile, 'wb')
        # wf.setnchannels(1)
        # wf.setsampwidth(2)
        # wf.setframerate(24000)
        
    def run(self):

        # audio_collection = b''
        while True:
            try:
                data = self.s.recv(512)
                logger.debug(f"Received: {len(data)}")
                self.stream.write(data)
                # audio_collection += data
                # wf.writeframes(data)
            except KeyboardInterrupt as e:
                logger.debug("Keyboard Interrupt")
                # stream.write(audio_collection)
                # time.sleep(2)
                # wf.close()
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
                break
            except Exception as e:
                print(e)

        self.s.close()
        
        
if __name__ == "__main__":
    speaking_thread = SpeakingThread()
    chunk_sender_thread = ChunkSenderThread()
    speaking_thread.start()
    chunk_sender_thread.run()
    


