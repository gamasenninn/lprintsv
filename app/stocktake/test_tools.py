import unittest
from tools.rfid_bar_tool import *
import tempfile

#辞書内のデータをソート
def normalize_dict_values_to_sets(d):
    return {k: set((v,) if not isinstance(v, tuple) else v) for k, v in d.items()}

#テストデータをHEX文字列に変換
def convert_to_file_data_hex(test_data):
    file_data = []
    for item in test_data:
        converted_item = ''.join([format(ord(char), 'x') for char in item])
        file_data.append(converted_item)
    return file_data

#一連の近傍検索のテスト
class TestFindClosestCodes(unittest.TestCase):
    
    def setUp(self):
        #一回目のテストデータ
        self.test_data = [
            "10001-1",
            "99991-1",
            "10001-2",
            "40001-5",
            "99991-3",
            "10001-10",
            "10001-11",
            "10001-12",
            "99991-4",
            "20001-13",
            "10001-14",
            "30001-7",
            "10001-8",
            "99991-2",
            "10001-15",
            "50001-16",
            "10001-6",
            "99991-5",
            "10001-17",
            "20001-3",
            "10001-4",
        ]

        #ニ回目のテストデータ
        self.test_data_2 = [
            "20001-1",
            "99992-1",
            "20001-3",
            "40002-1",
            "99992-2",
            "20001-10",
            "30001-11",
        ]

        # 一時的なディレクトリを作成しテストデータを作成する
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

        # 一時的なファイルにテストデータを書き込む
        self.test_file_path = os.path.join(self.test_dir.name, "test_file.txt")
        file_data = convert_to_file_data_hex(self.test_data)
        with open(self.test_file_path, 'w') as f:
            f.write("\n".join(file_data))

        # 一時的なファイルにテストデータを書き込む 2
        self.test_file_path2 = os.path.join(self.test_dir.name, "test_file_2.txt")
        file_data = convert_to_file_data_hex(self.test_data_2)
        with open(self.test_file_path2, 'w') as f:
            f.write("\n".join(file_data))

    # それぞれの関数を組み合わせてテスト
    def test_forward_and_reverse_results(self):
        self.maxDiff = None

        forward_result = find_closest_9999_codes(self.test_data)
        reverse_result = find_closest_9999_codes(self.test_data,reverse=True)
        merged_result = merge_forward_and_reverse_results(forward_result, reverse_result)
        ordered_result = order_by_original_data(merged_result, self.test_data)
        
        # 順読みと逆読みの結果が正しくマージされ、元のデータの並び順に整っているかテスト
        self.assertEqual(normalize_dict_values_to_sets(ordered_result), 
            normalize_dict_values_to_sets({
            '10001-1': ('99991-1', '99991-1'),
            '10001-2': ('99991-1', '99991-3'),
            '40001-5': ('99991-1', '99991-3'),
            '10001-10': ('99991-3', '99991-4'),
            '10001-11': ('99991-3', '99991-4'),
            '10001-12': ('99991-3', '99991-4'),
            '20001-13': ('99991-4', '99991-2'),
            '10001-14': ('99991-4', '99991-2'),
            '30001-7': ('99991-4', '99991-2'),
            '10001-8': ('99991-4', '99991-2'),
            '10001-15': ('99991-2', '99991-5'),
            '50001-16': ('99991-2', '99991-5'),
            '10001-6': ('99991-2', '99991-5'),
            '10001-17': ('99991-5', '99991-5'),
            '20001-3': ('99991-5', '99991-5'),
            '10001-4': ('99991-5', '99991-5')
        }))
    # グルーピングのための上位関数をテスト
    def test_group_place_results(self):
        self.maxDiff = None

        merged_result = group_place(self.test_data)
        
        # 順読みと逆読みの結果が正しくマージされ、元のデータの並び順に整っているかテスト
        self.assertEqual(normalize_dict_values_to_sets(merged_result),
            normalize_dict_values_to_sets({
            '10001-1': '99991-1',
            '10001-2': ('99991-1', '99991-3'),
            '40001-5': ('99991-1', '99991-3'),
            '10001-10': ('99991-3', '99991-4'),
            '10001-11': ('99991-3', '99991-4'),
            '10001-12': ('99991-3', '99991-4'),
            '20001-13': ('99991-4', '99991-2'),
            '10001-14': ('99991-4', '99991-2'),
            '30001-7': ('99991-4', '99991-2'),
            '10001-8': ('99991-4', '99991-2'),
            '10001-15': ('99991-2', '99991-5'),
            '50001-16': ('99991-2', '99991-5'),
            '10001-6': ('99991-2', '99991-5'),
            '10001-17': ('99991-5'),
            '20001-3': ('99991-5'),
            '10001-4': '99991-5'
        }))
    def test_read_rfid_make_group_dict(self):
        # print関数の出力をキャプチャ
        self.maxDiff = None
        with unittest.mock.patch("builtins.print") as mock_print:
            scode_dict = read_rfid_make_group_dict(self.test_file_path)
            #mock_print.assert_called_with(f"読み込みしました....{self.test_data[-1]}")
        
        # 順読みと逆読みの結果が正しくマージされ、元のデータの並び順に整っているかテスト
        self.assertEqual(normalize_dict_values_to_sets(scode_dict),
            normalize_dict_values_to_sets({
            #'10001-1': ('99991-1', '99991-1'),
            '10001-1': ('99991-1'),
            '10001-2': ('99991-1', '99991-3'),
            '40001-5': ('99991-1', '99991-3'),
            '10001-10': ('99991-3', '99991-4'),
            '10001-11': ('99991-3', '99991-4'),
            '10001-12': ('99991-3', '99991-4'),
            '20001-13': ('99991-4', '99991-2'),
            '10001-14': ('99991-4', '99991-2'),
            '30001-7': ('99991-4', '99991-2'),
            '10001-8': ('99991-4', '99991-2'),
            '10001-15': ('99991-2', '99991-5'),
            '50001-16': ('99991-2', '99991-5'),
            '10001-6': ('99991-2', '99991-5'),
            '10001-17': ('99991-5'),
            '20001-3': ('99991-5'),
            '10001-4': ('99991-5')
        }))
    def test_read_rfid_make_group_dict_pattern(self):
        self.maxDiff = None
        # print関数の出力をキャプチャ
        with unittest.mock.patch("builtins.print") as mock_print:
            test_file_pattern = os.path.join(self.test_dir.name, "*.txt")
            scode_dict = read_rfid_make_group_dict(test_file_pattern)
            #mock_print.assert_called_with(f"読み込みしました....{self.test_data[-1]}")
            self.assertEqual(normalize_dict_values_to_sets(scode_dict),
                normalize_dict_values_to_sets({
                '10001-1': ('99991-1'),
                '10001-2': ('99991-1', '99991-3'),
                '40001-5': ('99991-1', '99991-3'),
                '10001-10': ('99991-3', '99991-4'),
                '10001-11': ('99991-3', '99991-4'),
                '10001-12': ('99991-3', '99991-4'),
                '20001-13': ('99991-4', '99991-2'),
                '10001-14': ('99991-4', '99991-2'),
                '30001-7': ('99991-4', '99991-2'),
                '10001-8': ('99991-4', '99991-2'),
                '10001-15': ('99991-2', '99991-5'),
                '50001-16': ('99991-2', '99991-5'),
                '10001-6': ('99991-2', '99991-5'),
                '10001-17': ('99991-5'),
                '20001-3': ('99991-5'),
                '10001-4': ('99991-5'),
                '20001-1': ('99992-1'),
                '20001-3':('99992-1','99992-2','99991-5'),
                '40002-1':('99992-1','99992-2'),
                '20001-10':('99992-2'),
                '30001-11':('99992-2')
            }))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False,verbosity=2)
