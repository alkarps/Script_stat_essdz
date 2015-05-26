# -*- coding: utf8 -*-
u'''
Created on 13.10.2013
Last update on 13.05.2015

@author: alkarps

graphicsutil - библиотека генерации графиков.

List changes on 20.05.2015:
    1) Добавлена функция createGraphicByPoints, создающая файл с несколькими графиками, построенными по точкам. 
'''

import matplotlib.pyplot as plt;


def createGraphicByPoints(graphics, fileName, minX=None, maxX=None, minY=None, maxY=None, title=None, lableX=None, lableY=None):
    fig = plt.figure();
    if minX is not None and maxX is not None:
        plt.xlim(minX, maxX);
    if minY is not None and maxY is not None:
        plt.ylim(minY, maxY);
    if title is not None:
        plt.title(title);
    if lableX is not None:
        plt.xlabel(lableX);
    if lableY is not None:
        plt.ylabel(lableY);
    handlList = [];
    for graphic in graphics:
        hndl, = plt.plot(graphic[0], graphic[1], label = graphic[2]);
        handlList.append(hndl);
    plt.legend(handles=handlList, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    fig.savefig(fileName);
    plt.close();
