def deduplicate_by_key(docs, *keys):
    """
    根据指定的键值对列表进行去重。

    Parameters:
    - docs (list): 包含字典元素的文本列表。
    - *keys (str): 用于去重的字典键。

    Returns:
    - list: 去重后的文本列表。
    """

    seen_values = set()
    unique_docs = []

    for doc in docs:
        # 使用元组存储当前文档的键值组合
        key_values = tuple(doc.get(key) for key in keys)

        # 如果键值组合尚未出现过，则添加到去重后的列表中，并记录它的出现
        if key_values not in seen_values:
            seen_values.add(key_values)
            unique_docs.append(doc)

    return unique_docs

