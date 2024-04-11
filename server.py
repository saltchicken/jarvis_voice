from RealtimeTTS import TextToAudioStream, CoquiEngine
from loguru import logger
import socket, time

import threading, queue

from IPython import embed



class ChunkReceiverThread(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.queue = queue
        
    def run(self):
        self.socket.bind(('0.0.0.0', 10500))
        self.socket.listen()
        logger.debug("ChunkReceiver listening")
        receive_thread = threading.Thread(target=self.handle_client)
        receive_thread.start()
            
    def handle_client(self):
        conn, addr = self.socket.accept()
        logger.debug("ChunkReceiver connected")
        while True:
            data = conn.recv(1024)
            # logger.debug(f"Received: {data}")
            self.queue.put(data.decode())
         
            

class VoiceGenerator():
    def __init__(self):
        
        self.queue = queue.Queue()
        
        chunk_receiver = ChunkReceiverThread(self.queue)
        chunk_receiver.run()
        
        self.engine = CoquiEngine()
        format, a, b = self.engine.get_stream_info()
        
        self.stream = TextToAudioStream(self.engine)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', 10501))
        self.server_socket.listen(1)
        logger.debug('Waiting for connection')
        self.conn, addr = self.server_socket.accept()
        logger.debug("VoiceGenerator connected")
        
    def on_audio_chunk_callback(self, chunk):
        logger.debug(f"Chunk received:, len: {len(chunk)}")
        self.conn.sendall(chunk)
        
    def run(self):
        # TODO: Why is this initialization needed?
        self.stream.feed('a')
        self.stream.play_async(tokenizer="stanza", language="en", on_audio_chunk=lambda x: x, muted=True)
        # self.stream.feed("Test one")
        while True:
            text = self.queue.get()
            logger.debug(f"Text for TTS: {text}")
            self.stream.feed(text)
            self.stream.play_async(tokenizer="stanza", language="en", on_audio_chunk=self.on_audio_chunk_callback, muted=True)
        # embed()
        # time.sleep(3)
        # self.stream.feed('Test two')
        # self.stream.play(tokenizer="stanza", language="en", on_audio_chunk=self.on_audio_chunk_callback, muted=True)
        

if __name__ == "__main__":
    voice = VoiceGenerator()
    voice.run()

    
    
# from RealtimeTTS import TextToAudioStream, CoquiEngine

# def dummy_generator():
#     yield 'Hello there'

# def on_audio_chunk_callback(chunk):
#     print(f"Chunk received:, len: {len(chunk)}")

# if __name__ == "__main__":
#     engine = CoquiEngine()
#     stream = TextToAudioStream(engine)
#     print("streaming")
#     stream.feed("Hello")
#     stream.play_async(tokenizer="stanza", language="en", on_audio_chunk=on_audio_chunk_callback, muted=True)

    #stream.play_async()

