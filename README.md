# Azure AI Speech to Text

* Azure AI Speech Serviceの音声文字起こしサービスの利用方法について

## api
1. SpeechRecognizer（python SDK）- 単一発話認識。30秒以内の音声
2. ConversationTranscriber（python SDK）- 複数話者の話者分離可能。ストリームによるリアルタイム処理、非同期処理どちらも対応。ローカル音声ファイルの処理可能。ファイルサイズは1G未満。
3. バッチ文字起こしAPT（REST）- 長尺音声ファイルや複数ファイルの文字起こしバッチ処理用。ローカルファイル不可。Azure Blobに入っている音声ファイルを非同期で文字起こしを行う。

-> <b>ConversationTranscriberクラス(python)を用いて複数話者の会議音声の文字起こしを実装</b>

## 内容
1. youtubeで見つけた、経済に関する議論の音声ファイルをAzure SpeechのConversationTranscriberで文字起こしを実施してテキストファイルに保存。
2. 文字起こしでの話者判別がうまくいっていない箇所や会話の分割、漢字の誤変換などをLLM(gpt-o3-mini)にて修正。

## ファイル構成
* transcriber_module.py - 音声文字起こし関数のモジュールファイル。ConversationTranscriberクラスを読み込み、文字起こしを実施
* llm_text_corrector.py - 文字起こし結果のテキストをLLMで校正する関数のモジュールファイル。
* speech_to_text_and_modify.ipynb - 文字起こし関数と、文章校正関数を読み込んで音声の文字起こしから文章修正までを行っているnotebook
* audio_file/audio_long.WAV - 経済に関する議論の音声ファイル
* text_file/audi_long_to_text_result.txt - 音声文字起こし結果テキストファイル
* prompt/system_prompt.txt - LLMに文章校正を依頼するときのシステムプロンプト
* modified_text_file/modified_by_o3mini.txt - audi_long_to_text_result.txtの文章の校正結果
