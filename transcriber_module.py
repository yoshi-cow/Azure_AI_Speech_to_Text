# transcriber_module.py
import os
import azure.cognitiveservices.speech as speechsdk
import threading
from dotenv import load_dotenv


def transcribe_audio_file(
    audio_file_path: str, output_file_path: str, language: str = "ja-JP"
) -> list[str]:
    """
    音声ファイルを指定した言語で文字起こしし、結果をテキストファイルに保存する。

    Args:
        audio_file_path (str): 入力する音声ファイルのパス（例："audio_long.wav"）※ wavファイルのみ受け付ける。
        output_file_path (str): 文字起こし結果を書き出すテキストファイルのパス。
        language (str, optional): 音声認識の言語（デフォルトは"ja-JP"）。

    Returns:
        list[str]: 話者ごとの文字起こし結果を含むリスト。

    Raises:
        ValueError: 音声認識のAPIキーやエンドポイントが未設定の場合。
        Exception: 音声認識中のその他エラー。

    Example:
        >>> transcribe_audio_file("input.wav", "output.txt", language="ja-JP")
    """

    # 環境変数を読み込む
    load_dotenv()
    speech_key = os.getenv("SPEECH_KEY")
    service_region = os.getenv("SPEECH_REGION")
    speech_endpoint = os.getenv("SPEECH_ENDPOINT")
    # speech configと対象言語の設定
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, endpoint=speech_endpoint
    )
    speech_config.speech_recognition_language = language
    # 音声ファイルセット
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    # ConversationTranscrberクラスの初期化
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(
        speech_config=speech_config, audio_config=audio_config
    )

    # 文字起こし結果の保存用
    all_results = []
    # 文字起こし完了を通知するためのスレッド建てる
    transcription_done_event = threading.Event()

    def handle_transcribed(
        evt: speechsdk.transcription.ConversationTranscriptionEventArgs,
    ):
        """
        音声が認識され、文字起こしが完了したセグメントごとに呼び出されるコールバック関数。
        話者IDと共に結果を保存する。
        """
        # print(f"TRANSCRIBED: Text={evt.result.text} Speaker ID={evt.result.speaker_id}")
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            all_results.append(f"Speaker {evt.result.speaker_id}: {evt.result.text}")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            # 音声が認識できなかった場合（無音区間が長いなど）
            print(
                f"NOMATCH: Speech could not be recognized for this segment. Speaker: {evt.result.speaker_id}"
            )

    def handle_session_started(evt: speechsdk.SessionEventArgs):
        """セッション開始時に呼び出されるコールバック関数"""
        print(f"SESSION STARTED: {evt.session_id}")

    def handle_session_stopped(evt: speechsdk.SessionEventArgs):
        """セッション停止時に呼び出されるコールバック関数。"""
        print(f"SESSION STOPPED: {evt.session_id}")
        # 文字起こし完了の通知
        transcription_done_event.set()

    def handle_canceled(
        evt: speechsdk.transcription.ConversationTranscriptionCanceledEventArgs,
    ):
        """
        処理がキャンセルされた場合（エラー発生など）に呼び出されるコールバック関数。
        """
        print(f"CANCELED: Reason={evt.reason}")
        if evt.reason == speechsdk.CancellationReason.Error:
            print(f"CANCELED: ErrorCode={evt.error_code}")
            print(f"CANCELED: ErrorDetails={evt.error_details}")
        # 文字起こし完了（エラーによる終了）を通知
        transcription_done_event.set()

    # イベントハンドラを登録
    conversation_transcriber.transcribed.connect(handle_transcribed)
    conversation_transcriber.session_started.connect(handle_session_started)
    conversation_transcriber.session_stopped.connect(handle_session_stopped)
    conversation_transcriber.canceled.connect(handle_canceled)

    # 文字起こしの開始と待機
    print(f"Starting transcription for: {audio_file_path} ...")
    conversation_transcriber.start_transcribing_async()

    # trtanscription_done_eventがセットされる（処理が完了、またはエラーで停止する）まで待機する
    print("Transcription in progress...")
    transcription_done_event.wait()

    # 文字起こしの停止
    print("Stopping transcription...")
    stop_future = conversation_transcriber.stop_transcribing_async()
    # 停止処理の完了を待つ
    stop_future.get()
    print("Transcription stopped.")

    # 結果をファイルに書き出し
    with open(output_file_path, "w", encoding="utf-8") as f:
        for line in all_results:
            f.write(line + "\n")
    print(f"Transcription results saved to: {output_file_path}")

    return all_results
