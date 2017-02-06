# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 21:43:28 2017

@author: David
"""
from pathlib import Path
import os

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


#Python code for image manipulation and production for dicebeards

def create_dice_img(self, sides, value):
    '''Generates an image of a dice with the printed number value. Returns the
    file reference'''
    images = Path(os.path.dirname(__file__))
    num = int(value)
    
    dice_img = images / 'images' / ('d'+str(sides) + '.png')
    output_img = images / 'images' / 'output.png'
    
          
    #set the correct font size depending on dice
    font_sz = 20
    if int(sides) == 6:
        font_sz = 50
               
    #Printing of number on the dice 
    img = Image.open(str(dice_img))
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('arial.ttf', font_sz)
    #set x and y co-ordinates based on number
    W, H = img.size
    msg = str(num)
    w, h = draw.textsize(msg, font=font)
    x = (W-w)/2
    y = (H-h)/2
    
    draw.text((x,y),str(num),(255,255,255), font = font)
    img.save(str(output_img))
    
    #return the file
    return output_img



    
    
    
    