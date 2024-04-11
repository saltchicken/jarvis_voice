import socket
from loguru import logger
import pyaudio
import threading

class ChunkSenderThread():
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('192.168.1.100', 10500))
        
    def run(self):
        while True:
            user_input = input('Enter your speech')
            
            if user_input.lower() == 'quit':
                self.stop_event.set()
                break
            
            self.s.sendall(user_input.encode())
        logger.debug('Exiting ChunkSender')

class SpeakingThread(threading.Thread):
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event
        HOST = '192.168.1.100'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((HOST, 10501))
        
        self.p = pyaudio.PyAudio()
        CHANNELS = 1
        RATE = 12000
        self.stream = self.p.open(format=2, channels=CHANNELS, rate=RATE, output=True)
        
    def run(self):
        while not self.stop_event.is_set():
            try:
                data = self.s.recv(512)
                self.stream.write(data)
            except socket.timeout:
                continue
            
            except Exception as e:
                print(e)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.s.close()
        
        
if __name__ == "__main__":
    stop_event = threading.Event()
    speaking_thread = SpeakingThread(stop_event)
    chunk_sender_thread = ChunkSenderThread(stop_event)
    speaking_thread.start()
    chunk_sender_thread.run()
    


