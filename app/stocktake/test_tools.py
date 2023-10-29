import unittest
from tools.rfid_bar_tool import *
import tempfile

class TestFindClosestCodes(unittest.TestCase):
    
    def setUp(self):
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

        # 一時的なディレクトリを作成しテストデータを作成する
        self.file_data = [
            '31303030312d31',
            '39393939312d31',
            '31303030312d32',
            '34303030312d35',
            '39393939312d33',
            '31303030312d3130',
            '31303030312d3131',
            '31303030312d3132',
            '39393939312d34',
            '32303030312d3133',
            '31303030312d3134',
            '33303030312d37',
            '31303030312d38',
            '39393939312d32',
            '31303030312d3135',
            '35303030312d3136',
            '31303030312d36',
            '39393939312d35',
            '31303030312d3137',
            '32303030312d33',
            '31303030312d34'
        ]

        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

        # 一時的なファイルにテストデータを書き込む
        self.test_file_path = os.path.join(self.test_dir.name, "test_file.txt")
        with open(self.test_file_path, 'w') as f:
            f.write("\n".join(self.file_data))

    
    def test_forward_and_reverse_results(self):
        forward_result = find_closest_9999_codes_with_lookahead(self.test_data)
        reverse_result = find_closest_9999_codes_reverse_with_lookahead(self.test_data)
        merged_result = merge_forward_and_reverse_results(forward_result, reverse_result)
        ordered_result = order_by_original_data(merged_result, self.test_data)
        
        # 順読みと逆読みの結果が正しくマージされ、元のデータの並び順に整っているかテスト
        self.assertEqual(ordered_result, {
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
        })
    def test_group_place_results(self):
        merged_result = group_place(self.test_data)
        
        # 順読みと逆読みの結果が正しくマージされ、元のデータの並び順に整っているかテスト
        self.assertEqual(merged_result, {
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
        })
    def test_read_rfid_make_group_dict(self):
        # print関数の出力をキャプチャ
        with unittest.mock.patch("builtins.print") as mock_print:
            scode_list = read_rfid_make_group_dict(self.test_file_path)
            mock_print.assert_called_with(f"読み込みしました....{self.test_data[-1]}")
        # 検証
        self.assertEqual(scode_list, [f"{x}" for x in self.test_data])

        merged_result = group_place(scode_list)
        
        # 順読みと逆読みの結果が正しくマージされ、元のデータの並び順に整っているかテスト
        self.assertEqual(merged_result, {
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
        })
    def test_read_rfid_make_group_dict_pattern(self):
        # print関数の出力をキャプチャ
        with unittest.mock.patch("builtins.print") as mock_print:
            test_file_pattern = os.path.join(self.test_dir.name, "*.txt")
            scode_list = read_rfid_make_group_dict(test_file_pattern)
            mock_print.assert_called_with(f"読み込みしました....{self.test_data[-1]}")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False,verbosity=2)
