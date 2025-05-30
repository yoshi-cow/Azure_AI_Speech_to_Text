# Azure AI Speech to Text

* Azure AI Speech Serviceの音声文字起こしサービスの利用方法について
  * Speech ServiceはバックグラウンドでOpenAIのWhisperモデルを利用している
  * 音声ファイルの形式は"wav"推奨
  * 補：OpenAIの最新モデルGPT-4o-Transcribeは25MBまでのファイルしか対応していないため、数十分の会話ファイルだと容量が大きくて厳しいため、今回は検討外。

## api
1. SpeechRecognizer（python SDK）- 単一発話認識。30秒以内の音声
2. ConversationTranscriber（python SDK）- 複数話者の話者分離可能。ストリームによるリアルタイム処理、非同期処理どちらも対応。ローカル音声ファイルの処理可能。ファイルサイズは1G未満。
3. バッチ文字起こしAPT（REST）- 長尺音声ファイルや複数ファイルの文字起こしバッチ処理用。ローカルファイル不可。Azure Blobに入っている音声ファイルを非同期で文字起こしを行う。

-> <b>ConversationTranscriberクラス(python)を用いて複数話者の会議音声の文字起こしを実装</b>

## Azure AI Speechサービスの払い出しについて
* 以前は、リソースから『音声』サービスをデプロイしていたが、2025/5よりAI Foundryに統一され、AI Foundryプロジェクトの「モデル+エンドポイント」→「サービスエンドポイント」の『Azure AI 音声』から、キーとエンドポイントを取得。

## 内容
1. youtubeで見つけた経済に関する議論の音声ファイルを、Azure SpeechのConversationTranscriberで文字起こしを実施してテキストファイルに保存。
   * 結果：
     * 話者分離がうまくいっていない文章あり。
     * 会話の区切りを正しく認識していない箇所が複数あり。
2. 文字起こしでの話者判別がうまくいっていない箇所や会話の分割、漢字の誤変換などをLLM(gpt-o3-mini)にて修正。
   * 結果：
     * プロンプトの修正により、話者分離の修正や会話の区切りの補正が大分できるようになった。
     * LLMの課題となっている再現性の確保の問題が発生。(tempratureの設定など必要)

## ファイル構成
* transcriber_module.py - 音声文字起こし関数のモジュールファイル。ConversationTranscriberクラスを読み込み、文字起こしを実施
* llm_text_corrector.py - 文字起こし結果のテキストをLLMで校正する関数のモジュールファイル。
* speech_to_text_and_modify.ipynb - 文字起こし関数と、文章校正関数を読み込んで音声の文字起こしから文章修正までを行っているnotebook
* audio_file/audio_long.WAV - 経済に関する議論の音声ファイル
* text_file/audi_long_to_text_result.txt - 音声文字起こし結果テキストファイル
* prompt/ - LLMに文章校正を依頼するときのシステムプロンプト(校正結果をLLMにチェック＆プロンプトの修正を依頼して、3番目のプロンプトで落ち着いた。4番目だと指示が細かすぎて悪化。)
  * system_prompt_1.txt / system_prompt_2.txt / system_prompt_3.txt / system_prompt_4.txt
* modified_text_file/ - audi_long_to_text_result.txtの文章の校正結果。システムプロンプトごとに出力
