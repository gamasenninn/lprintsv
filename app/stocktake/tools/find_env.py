import os
from dotenv import load_dotenv

def find_dotenv():
    # 現在のディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # ルートディレクトリに到達するまでループ
    while current_dir != os.path.dirname(current_dir):
        # .env ファイルのパスを生成
        dotenv_path = os.path.join(current_dir, '.env')
        
        # .env ファイルが存在するか確認
        if os.path.isfile(dotenv_path):
            return dotenv_path

        # 一つ上のディレクトリに移動
        current_dir = os.path.dirname(current_dir)
    
    # .env ファイルが見つからなかった場合
    return None


if __name__ == '__main__':
    # .env ファイルを探す
    dotenv_path = find_dotenv()

    # .env ファイルが見つかった場合、それを読み込む
    if dotenv_path:
        load_dotenv(dotenv_path)
        # すべての環境変数を表示
        for key, value in os.environ.items():
            print(f'{key}: {value}')
        
