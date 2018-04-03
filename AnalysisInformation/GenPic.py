#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf')
import matplotlib.pyplot as plt
import numpy as np
def genHistogrampic(data={}, xlabel="x", ylabel="y", title="default"):
    '生成条形图'
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体,解决中文显示问题
    n_groups = len(data.keys())
    datavalue = data.values()
    fig, ax = plt.subplots(figsize=(22, 10))
    index = np.arange(n_groups)
    # bar_width = 0.35
    bar_width = 0.2
    opacity = 0.4
    error_config = {'ecolor': '0.3'}
    rects1 = plt.bar(index, datavalue, bar_width,
                     alpha=opacity,
                     color='b',
                     # yerr=std_men,
                     error_kw=error_config,
                     label='datavalue')

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2.0, 1.05 * height,
                    '%d' % int(height), ha='center', va='bottom')

    autolabel(rects1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(index + bar_width, data.keys())
    plt.tight_layout()
    plt.show()



def genPiechartpic( data={}, title="default"):
    '生成饼图'
    # 调节图形大小，宽，高
    plt.figure(figsize=(16, 19))
    # 定义饼状图的标签，标签是列表
    labels = data.keys()
    # 每个标签占多大，会自动去算百分比
    sizes = data.values()
    patches, l_text, p_text = plt.pie(sizes, labels=labels, labeldistance=1.05, autopct='%3.1f%%', shadow=False,
                                      startangle=20, pctdistance=0.7)
    for t in l_text:
        t.set_size = (1)
    for t in p_text:
        t.set_size = (1)
    plt.axis('equal')
    plt.show()