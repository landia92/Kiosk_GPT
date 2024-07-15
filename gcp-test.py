from openai import OpenAI


class gpt_speech_class:
    def __init__(self):
        self.client = OpenAI(api_key="")

        self.structured_message = [{"role": "system", "content": """You are a helpful café clerk. Customers chat, 
            so not all inputs will be orders. If an input is not an order, you must return only [this is not an order] 
            and ignore it. If the input is an order, you should take the order. 
            The order must include the type of coffee, the size of the coffee, and the quantity. 
            If the customer forgets to provide specific details, you should ask them for the missing information. 
            Structure the order like this: {type: {type}, size: {size}, quantity: {quantity}}. 
            If the order is complete, you must return only the order."""}]

    def call_gpt(self, input_string: str):
        self.structured_message.append({"role": "user", "content": input_string})

        chat_completion = self.client.chat.completions.create(
            messages=self.structured_message,
            model="gpt-4o"
        )
        print(chat_completion.choices[0].message.content)
        return chat_completion.choices[0].message.content

import sys
from google.cloud import speech
import pyaudio
from six.moves import queue
import os

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self._closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self._closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self._closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self._closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses, gpt_speech):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if result.is_final:
            print(transcript + overwrite_chars)

            # 음성 인식 결과를 GPT-4로 전달
            gpt_speech.call_gpt(transcript + overwrite_chars)

            num_chars_printed = 0
        else:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

def main():
    client = speech.SpeechClient()

    gpt_speech = gpt_speech_class()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="ko-KR",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses, gpt_speech)

if __name__ == "__main__":
    main()
