# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:26:17 2017

@author: David
"""
import dice
import random

from pathlib import Path
import re

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class Coin:
    '''Class for implementing the python dice and producing images in Telegram'''
    
    def __init__(self, images_folder, mode = 'pic'):
        self.images_path = Path(images_folder)
        self.mode = mode
                    
    def flip_coin(self,input_string):
        '''Rolls the dice and produces output as defined in mode'''
        #Extract only the first number from the input string
        input_args = input_string.split(" ")
        command = int(input_args[0])
        
        #Flip the coins
        coin_out = self.flip(command)      
        total_H = sum(coin_out)
        total_T = command-sum(coin_out)
        
        #Check the output the user wants and give it
        if self.mode == 'pic':
            #create and return the combined image
            try:
                out_img = self.mode_pic(coin_out,total_H, total_T)
                final_img = self.images_path / ('final.png')
                out_img.save(str(final_img))
                return final_img
            except FileNotFoundError:
                return self.mode_txt(coin_out, total_H, total_T)
        elif self.mode == 'icon':
            return ''
        else:
            #convert the rolls into strings
            return self.mode_txt(coin_out, total_H, total_T) 
        
        
    def flip(self, n):
        '''Flip a coin n times'''
        results = []
        for i in range(0,n):
            #Heads is equivalent to 1, tails to 0
            results.append(random.randint(0,1))
        return results
                

    def mode_pic(self, coin_out, heads, tails):
        '''Generates an image of a dice with the printed number value. Returns the
        image'''     
        H_img = self.images_path / 'H.png'
        T_img = self.images_path / 'T.png'
        
        #Calculate the required image size and make it
        coins_flipped = heads + tails 
        if coins_flipped == 1:
            out_img_size = [100,150]
        elif coins_flipped < 3:
            out_img_size = [300,150]
        elif coins_flipped < 5:
            out_img_size = [100*coins_flipped,150] #extra 50 for total
        else:
            out_img_size = [500,100*int((coins_flipped-1)/5)+150] #extra 50 for total
    
        #Create the image to be output
        out_img = Image.new('RGBA', out_img_size) 
        
        x_offset = 0
        y_offset = 0
        for flip in coin_out:
            output_img = Image
            if flip:
                output_img = Image.open(str(H_img))
            else:
                output_img = Image.open(str(T_img))            
            out_img.paste(output_img,(x_offset,y_offset)) 
            
            x_offset += 100
            if x_offset > 400:
                x_offset = 0
                y_offset += 100
        
        #Add text giving the total roll to the bottom
        msg = ''
        if heads+tails>1:
            msg = 'Heads: ' + str(heads) + ' Tails: ' + str(tails)
        elif heads == 1:
            msg = 'Heads'
        elif tails == 1:
            msg = 'Tails'
        
        draw = ImageDraw.Draw(out_img)
        font = ImageFont.truetype('arial.ttf', 36)
        w, h = draw.textsize(msg, font=font)
        draw.text(((out_img_size[0]-w)/2,out_img_size[1]-50),msg,(0,0,0), font = font)
        
        return out_img    
 
    
    def mode_txt(self, coin_out, heads, tails):
        #convert the flips into  a string
        out_str = ''
        for flip in coin_out:
            if flip:
                out_str = out_str + 'H '
            else:
                out_str = out_str + 'T '
        
        out_str = out_str+'= [H:'+str(heads)+', T:'+str(tails)+']'
        return out_str

                

            
        
        
    
    
        
        
        
        
        
        
    
    