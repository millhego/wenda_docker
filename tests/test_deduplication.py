import unittest
from plugins.utils.deduplicate_by_key import deduplicate_by_key

class TestDeduplicateByKey(unittest.TestCase):

    def test_deduplicate_by_key_single_key(self):
        # 测试用例1：根据 "memory_name" 去重
        docs1 = [
            {"id": 1, "memory_name": "文本1"},
            {"id": 2, "memory_name": "文本2"},
            {"id": 3, "memory_name": "文本3"},
            {"id": 1, "memory_name": "文本1"},  # 重复项
            {"id": 4, "memory_name": "文本4"},
            {"id": 2, "memory_name": "文本2"},  # 重复项
            # ... 更多文本
        ]
        unique_docs1 = deduplicate_by_key(docs1, "memory_name")
        self.assertEqual(len(unique_docs1), 4)  # 去重后应该有4个元素

    def test_deduplicate_by_key_multiple_keys(self):
        # 测试用例2：根据 "id" 和 "memory_name" 组合去重
        docs2 = [
            {"id": 1, "memory_name": "文本1"},
            {"id": 2, "memory_name": "文本2"},
            {"id": 3, "memory_name": "文本3"},
            {"id": 1, "memory_name": "文本1"},  # 重复项
            {"id": 4, "memory_name": "文本4"},
            {"id": 2, "memory_name": "文本2"},  # 重复项
            # ... 更多文本
        ]
        unique_docs2 = deduplicate_by_key(docs2, "id", "memory_name")
        self.assertEqual(len(unique_docs2), 4)  # 去重后应该有4个元素

    def test_deduplicate_by_key_empty_list(self):
        # 测试用例3：空列表，期望返回空列表
        docs3 = []
        unique_docs3 = deduplicate_by_key(docs3, "id", "memory_name")
        self.assertEqual(len(unique_docs3), 0)

    def test_deduplicate_by_key_single_document(self):
        # 测试用例4：只有一个文档的情况
        docs4 = [{"id": 1, "memory_name": "文本1"}]
        unique_docs4 = deduplicate_by_key(docs4, "id", "memory_name")
        self.assertEqual(len(unique_docs4), 1)

if __name__ == '__main__':
    unittest.main()