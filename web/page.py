# !/user/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------
# 文件：page.py
# 描述：翻页
# 版本：0.1
# 作者：lg
# 日期：2017-11-08
# --------------------------------------------------------

import math

def getPage(count, index=1, limit=10):
    '''
    :param limit: 每页大小
    :param index: 请求页数
    :param count: 总记录数
    :return: 
                count:  总记录数
                offset: 跳过记录
                size:   总页数
                limit:  每页大小
                index： 当前页数
    '''
    page =dict()
    # 每页大小
    if isinstance(limit, int):
        page_limit = limit
    else:
        page_limit = int(limit)

    # 当前页数
    if isinstance(index, int):
        page_index = index
    else:
        page_index = int(index)

    # 总记录数
    if isinstance(count, int):
        page_count = count
    else:
        page_count = int(count)

    # 总页数
    page_size = math.ceil(count / page_limit)
    if page_size < 1:
        page_size = 1

    # 跳过记录
    if page_index <= page_size:
        page_offset = (page_index - 1) * page_limit
    else:
        page_offset = 0
    return {
        'count': page_count,
        'limit': page_limit,
        'size': page_size,
        'offset': page_offset,
        'index': page_index
        }