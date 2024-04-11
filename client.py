import socket
from loguru import logger
import pyaudio
import threading

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
        
        HOST = '192.168.1.100'
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.s.connect((HOST, 10501))
        
        self.p = pyaudio.PyAudio()
        CHANNELS = 1
        RATE = 12000
        self.stream = self.p.open(format=2, channels=CHANNELS, rate=RATE, output=True)
        
    def run(self):
        while True:
            try:
                data = self.s.recv(512)
                self.stream.write(data)
            except KeyboardInterrupt as e:
                logger.debug("Keyboard Interrupt")
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
                break
            except socket.timeout:
                continue
            
            except Exception as e:
                print(e)

        self.s.close()
        
        
if __name__ == "__main__":
    speaking_thread = SpeakingThread()
    chunk_sender_thread = ChunkSenderThread()
    speaking_thread.start()
    chunk_sender_thread.run()
    


