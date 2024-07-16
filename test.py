import wave
import io
from openai import OpenAI
from google.cloud import texttospeech

class gcp_speak:
    def synthesize_speech(text):
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        return response.audio_content

    def play_audio(audio_content):
        wf = wave.open(io.BytesIO(audio_content), 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()



class gpt_speech_class:
    def __init__(self):
        self.client = OpenAI(api_key="키")

        self.structured_message = [
            {"role": "system", "content": "당신은 카페 직원입니다. " # system 역할로, AI의 행동을 지시->카페 직원
                                  "당신 앞에 고객이 있습니다. "
                                  "고객은 한국인일 가능성이 높습니다."

                                  # 시스템 메시지에 예외 상황 처리 추가
                                  "고객이 주문과 관련 없는 질문을 한다면, "
                                  "예를 들어 카페 정보, 위치, 영업 시간 등을 물어보면, 도움 되는 답변을 제공하세요. "
                                  "카페와 완전히 무관한 질문이라면, "
                                  "정중하게 카페 관련 문의만 도와드릴 수 있다고 알려주세요. "

                                  "당신은 주문을 받아야 합니다. "
                                  "카페에는 각 카테고리마다 여러 메뉴 항목이 있습니다. "
                                  "메뉴 항목이 포함되어야 하며, 메뉴 항목 없이 주문할 수 없습니다. "

                                  # 주문 취소
                                  "고객은 주문 과정 중 언제든지 주문을 취소할 수 있습니다. "

                                  "메뉴의 온도(뜨겁게 또는 차갑게), 크기, 수량 등의 주문 세부 사항을 물어보세요. "
                                  "고객이 특정 세부 사항을 말하는 것을 잊었다면, 다시 물어보세요. "
                                  "고객이 이미 세부 사항을 지정했다면, 다시 묻지 마세요. "
                                  "주문을 다음과 같이 구조화하세요: "
                                  "{타입: {type}, 온도: {temperature}, 크기: {size}, 수량: {quantity}, 가격: {price}} "
                                  "주문 내역을 출력할 때는 이 구조를 유지하세요."

                                  "주문이 완료되면, 주문만 반환해야 합니다. "

                                  "한 메뉴 항목의 주문을 완료한 후, 고객은 다른 항목을 선택할 수 있습니다. "
                                  "따라서, 추가로 주문할 것이 있는지 물어보세요. "

                                  # 주문 요약 및 최종 확인
                                  "고객이 더 이상 주문할 것이 없다고 말하면, "
                                  "주문 세부 사항과 총 가격을 반복하여 확인을 요청하세요. "
                                  # 최종 주문 키워드
                                  "고객이 주문 확인이 맞다는 응답을 하면, "
                                  "'Order Complete'와 주문 내역을 출력하여 주문 과정이 완료되었음을 자동으로 표시하세요."

     },
    {"role": "assistant", "content": "안녕하세요. 주문을 도와드릴까요?"} #assistant 역할로, 처음 사용자에게 보일 인사 메시지를 설정
]

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
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "키"

class MicrophoneStream(object):
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

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

    teller = gcp_speak()

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


            answer = gpt_speech.call_gpt(transcript + overwrite_chars)
            audio_content = teller.synthesize_speech(answer)
            teller.play_audio(audio_content)


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
        model="telephony"
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
