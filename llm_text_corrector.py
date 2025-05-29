# llm_text_corrector.py
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

def correct_text_with_llm(
    system_prompt_file: str,
    user_message_file: str,
    output_file: str,
    print_response: bool = True,
):
    """
    LLM（Azure OpenAI）を用いて、テキスト修正タスクを実行し、結果をファイルに保存する関数。

    Args:
        system_prompt_file (str): システムメッセージ（プロンプト）ファイルのパス
        user_message_file (str): ユーザー発話テキスト（例：文字起こし結果）ファイルのパス
        output_file (str): LLMの出力を書き込むファイルのパス
        print_response (bool): レスポンスをprintで表示するかどうか（デバッグ用）

    Returns:
        str: LLMからの生成テキスト
    """
    load_dotenv()

    # 各種API情報を環境変数から取得
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_DEPLOYMENT")
    subscription_key = os.getenv("AZURE_OPENAI_SUBSCRIPTIONKEY")

    # プロンプトとユーザーメッセージを読み込み
    with open(system_prompt_file, encoding="utf-8") as f:
        system_prompt = f.read()
    with open(user_message_file, encoding="utf-8") as f:
        ori_text = f.read()

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=subscription_key,
    )

    print("-call LLM...-\n")

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ori_text}
        ],
        model=deployment
    )

    result_text = response.choices[0].message.content
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result_text)
    
    print("-fin.-\n")

    if print_response:
        print(f"LLM response written to {output_file}")
        print(result_text[:500])  # 最初の500文字だけ表示

    return result_text
