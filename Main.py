import pygame
pygame.init()
import math
import os
import random
import json

pygame.display.set_caption("Tournament Creator")
pygame.display.set_icon(pygame.Surface((0,0)))

from TextBox import TextBox

FontTinyBold = pygame.font.SysFont("Calibri",16,True)
FontTiny = pygame.font.SysFont("Calibri",16)
FontSmallBold = pygame.font.SysFont("Calibri",20,True)
FontSmall = pygame.font.SysFont("Calibri",20)
FontMediumSmallBold = pygame.font.SysFont("Calibri",30,True)
FontMediumSmall = pygame.font.SysFont("Calibri",30)
FontNormal = pygame.font.SysFont("Calibri",40)
FontNormalBold = pygame.font.SysFont("Calibri",40,True)
FontMediumLargeBold = pygame.font.SysFont("Calibri",60,True)
FontMediumlarge = pygame.font.SysFont("Calibri",60)
FontLargeNormal = pygame.font.SysFont("Calibri",80)
FontLargeNormalBold = pygame.font.SysFont("Sans Serif",80,True)

CamX = 0
CamY = 0

MainMenu = True

contestant_names = []

Contestant_Icons = []
Match_Icons = []


Mask_Color = (9,35,35)

Contestant_Base = pygame.image.load("Contest_base.png")
Contestant_Mask = pygame.image.load("Contest_mask.png")
Match_Base = pygame.image.load("Match_base.png")
Match_Mask = pygame.image.load("Match_mask.png")
Highlighted = pygame.Surface((48,48))
Highlighted.fill((255,255,255))
Highlighted.set_alpha(80)
Eliminated = pygame.Surface((48,48))
Eliminated.fill((0,0,0))
Eliminated.set_alpha(120)

Info_Image = pygame.image.load("Info_Image.png")

remaining_contestants = 0
remaining_matches = 0
pregame_matches = 0
next_match = None
eliminated_contestants = 0
completed_matches = 0
total_contestants = 0
total_matches = 0
Error = None
Error_Time = 0

EditMode = False
Edit_Image = pygame.image.load("Edit.png")


SelectedBlock = None
MovingBlock = None

TimeSinceSelected = 0



def save(name):
    if name=="":
        set_error("Please enter a name to save to!")
        return
    if not os.path.exists("./saves/"):
        os.mkdir("./saves")
    if not os.path.isfile("./saves/"+name+".json"):
        open("./saves/"+name+".json","x").close()
    
    s = open("./saves/"+name+".json","w+")
    json.dump([[y.get_data() for y in x] for x in blocks],s)
    s.close()
def load(name):
    global blocks
    if not os.path.exists("./saves/"):
        set_error("Save a file first!")
        return
    if not os.path.isfile("./saves/"+name+".json"):
        set_error("That file doesn't exist!")
        return
    s = open("./saves/"+name+".json")
    l = json.load(s)
    blocks = [[] for x in range(len(l))]
    for x in range(len(l)): #setup blocks
        for y in range(len(l[x])):
            v = l[x][y]
            if v==None:
                blocks[x].append(Blank(y,x))
            else:
                if v["type"]=="c":
                    blocks[x].append(Contestant(v["value"],v["color"],y,x))
                elif v["type"]=="m":
                    blocks[x].append(Match(y,x,None))
                else:
                    blocks[x].append(Block(y,x,None))
    for x in range(len(l)): #setup block in-/out-put
        for y in range(len(l[x])):
            v = l[x][y]
            if v==None:
                continue
            if v["type"]=="m":
                blocks[x][y].input = [blocks[x-1][z] for z in v["in"]]
                blocks[x][y].winner = v["winner"]
            if v["out"]!=None:
                blocks[x][y].output = blocks[x+1][v["out"]]
    blocks[len(blocks)-1][0].propigate_out(False)
    s.close()


def reset_stats():
    global remaining_contestants
    global remaining_matches
    global pregame_matches
    global next_match
    global eliminated_contestants
    global completed_matches
    global total_contestants
    global total_matches
    remaining_contestants = 0
    remaining_matches = 0
    pregame_matches = 0
    next_match = None
    eliminated_contestants = 0
    completed_matches = 0
    total_contestants = 0
    total_matches = 0



def dist(a,b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
def Text(text = "",color = (255,255,255),pos = (0,0),font = FontSmallBold,PosType = (1,0),background=None,scr=None):
    img = scr if scr!=None else screen
    text = font.render(text, True, color)
    if len(color) > 3:
        text.set_alpha(color[3])
    text_rect = text.get_rect()
    if PosType[0] == 0:
        text_rect.x = pos[0]
    elif PosType[0] == 1:
        text_rect.centerx = pos[0]
    if PosType[1] == 0:
        text_rect.y = pos[1]
    elif PosType[1] == 1:
        text_rect.centery = pos[1]
    if background!=None:
        if len(background)>3:
            s = pygame.Surface([text_rect[2]+10,text_rect[3]+5])
            s.fill(Mask_Color)
            s.set_colorkey(Mask_Color)
            pygame.draw.rect(s,background,[0,0,text_rect[2]+10,text_rect[3]+5],border_radius=5)
            s.set_alpha(background[3])

            img.blit(s,[text_rect[0]-5,text_rect[1]-3])
        else:
           pygame.draw.rect(img,background,[text_rect[0]-5,text_rect[1]-2,text_rect[2]+10,text_rect[3]+5],border_radius=5)
        img.blit(text, text_rect)


class Block():
    def __init__(self,index,column,input):
        self.render_time = 0
        self.out = False
        self.index = index
        self.column = column
        self.input = input
        self.output = None
        self.clicked = False
        self.clicked_time = 0
        self.pos = [0,calc_pos(column,index)[1]]
        self.color_new = (0,0,0)
        
    def propigate_out(self,val):
        if self.output!=None:
            self.output.propigate_out(val)
        else:
            global remaining_contestants
            global eliminated_contestants
            global remaining_matches
            global pregame_matches
            global completed_matches
            global next_match
            global contestants
            global total_contestants
            global total_matches
            contestants=0
            total_contestants=0
            total_matches=0
            remaining_contestants = 0
            eliminated_contestants = 0
            remaining_matches = 0
            completed_matches = 0
            pregame_matches = 0
            next_match = None
            self.update_out(val)
            a = False
            for c in blocks:
                if a:
                    break
                for b in c:
                    if a:
                        break
                    if isinstance(b,Match):
                        if b.winner==-1:
                            next_match = b
                            a = True
    def get_color(self):
        return self.color_new
    def get_val(self):
        return ""
    def get_data(self):
        return {"type":("c" if isinstance(self,Contestant) else ("m" if isinstance(self,Match) else "d")),"in":[x.index for x in self.input] if self.input != None else None,"out":self.output.index if self.output!=None else None}
    def update(self,events):
        global SelectedBlock
        global MovingBlock
        if SelectedBlock == None and MovingBlock == None:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x = self.column
                    y = self.index
                    p = list(self.pos)
                    
                    if dist(pygame.mouse.get_pos(),p)<25 and pygame.mouse.get_pressed()[0]:
                        if EditMode:
                            self.clicked = True
                            #add code to make it start moving the object
                            # the objects that need to move are equivalent to the objects between 2**(difference between the column of the object, and column of the objects being moved)*index of object and 2**(difference between the column of the object, and column of the objects being moved)*index of object + (2**(diff)-1)
                            # move from a to b
                            # make a function which goes through every object and sets its column and index to its column and index in the blocks list
                        else:
                            if self.output!=None and isinstance(self.output,Match):
                                if self.output.winner!=self.output.input.index(self):
                                    if self.column+1>(next_match.column if next_match!=None else -1) and self.output.winner==-1:
                                        set_error("Finish all matches in row "+str(next_match.column))
                                    else:
                                        
                                        if self.output.val!=0 and self.output.old_winner==self.output.input.index(self):
                                            self.output.val=1-self.output.val
                                        self.output.old_winner=self.output.winner
                                        # if self.output.old_winner==self and self.output.winner!=-1:
                                        #     self.output.old_winner=self.output.winner
                                        #     self.output.val=1-self.output.val
                                        self.output.winner = self.output.input.index(self)
                                        self.propigate_out(False)
                                else:
                                    if self.output.val!=0 and self.output.old_winner!=self.output.input.index(self):
                                        self.output.val=1-self.output.val
                                    self.output.old_winner=self.output.winner
                                    self.output.winner = -1
                                    self.propigate_out(False)
                if event.type == pygame.MOUSEBUTTONUP:
                    #add code to make it stop moving the object
                    if self.clicked and self.clicked_time<=15:
                        SelectedBlock = self
                    self.clicked = False
                        
            if self.clicked:
                self.clicked_time+=1
            else:
                self.clicked_time = 0
            if self.clicked_time>15 and self.clicked and pygame.mouse.get_pressed()[0]:
                MovingBlock = self
                self.clicked_time=30
            elif self.clicked_time>5 and self.clicked and pygame.mouse.get_pressed()[0] and dist(self.pos,pygame.mouse.get_pos())>30:
                MovingBlock = self
                self.clicked_time=30
            if not pygame.mouse.get_pressed()[0] and self.clicked:
                if self.clicked and self.clicked_time<=15:
                    SelectedBlock = self
                self.clicked = False
    def set_output(self,output):
        self.output = output
    def update_out(self,val):
        self.out = val
        if isinstance(self,Match):
            global total_matches
            total_matches+=1
            index = 0
            for i in self.input:
                if (index == self.winner or self.get_val()=="" or i.get_val()=="") and not val:
                    i.update_out(False)
                else:
                    i.update_out(True)
                index +=1
            if self.out or self.winner!=-1:
                global completed_matches
                completed_matches += 1
            else:
                global remaining_matches
                global pregame_matches
                remaining_matches += 1
                if self.column==1:
                    pregame_matches +=1
        else:
            global total_contestants
            global contestants
            contestants+=1
            total_contestants=contestants
            if self.out:
                global eliminated_contestants
                eliminated_contestants += 1
            else:
                global remaining_contestants
                remaining_contestants += 1
    def render(self):
        x = self.column
        y = self.index
        p = list(calc_pos(x,y))
        self.pos[0] = self.pos[0]*0.9+p[0]*0.1
        self.pos[1] = self.pos[1]*0.9+p[1]*0.1
        # self.pos = p
        p=self.pos

        colorn = self.color_new
        if isinstance(self,Match):
            if self.winner!=-1:
                colorn = self.input[self.winner].get_color()
            else:
                colorn = (200,200,200)
        elif isinstance(self,Contestant):
            colorn = self.color
            if self.out and not EditMode:
                colorn = combine(colorn,(50,50,50),0.3)
        
        self.color_new = combine(self.color_new,colorn,0.8)
        






        if self.input!=None:
            if not (-40<self.input[1].pos[1] and self.input[0].pos[1]<screen.get_height()+40):
                return
        else:
            if not -40<self.pos[1]<screen.get_height()+40:
                return
        color = self.get_color()
        val = self.get_val()
        if dist(pygame.mouse.get_pos(),p)<25:
            color = combine(color,(255,255,255),0.5)
        
        image = None
        mask = None
        if isinstance(self,Match):
            if self.input !=None:
                if self.winner!=self.old_winner:
                    v = self.val
                    self.val = self.val+0.04
                    if self.val>=0.99:
                        self.val = 0
                        self.old_winner = self.winner
                else:
                    if self.val>0:
                        self.val = 0
                    if self.val<0:
                        self.val = 0
                i = 0
                val_v = ((self.val**2)*2 if self.val<0.5 else ((self.val-1)**2)*-2+1)
                for b in self.input:
                    c = list(b.pos)
                    p3 = list(calc_pos(b.column,b.index))
                    c[0] = c[0]*0.9+p3[0]*0.1
                    c[1] = c[1]*0.9+p3[1]*0.1
                    p2 = list(p)
                    p2[1]+=i*(30/len(self.input))-7
                    col1 = b.get_color()
                    col2 = col1[:]
                    col3 = (0,0,0)
                    col4 = col3[:]
                    # if b.out:
                    #     col1 = combine(col1,(0,0,0),0.5)
                    # if (self.old_winner!=i and self.old_winner!=-1) or self.out:
                    #     col2 = combine(col2,(0,0,0),0.5)
                    if self.winner==i:
                        col3 = col1[:]
                    if self.old_winner==i:
                        col4 = col2[:]
                    if self.winner==i:
                        line(c,p2,col1,9,color2=col2,val=val_v)
                        line(c,p2,col3,7,color2=col4,val=val_v)
                    else:
                        line(p2,c,col1,9,color2=col2,val=val_v)
                        line(p2,c,col3,7,color2=col4,val=val_v)
                    
                    
                    # line(p2,c,(0,0,0))

                    # if not self.out and (self.winner==i or self.get_val()=="" or b.get_val()==""):
                    #     # if self.winner==-1:
                    #     #     if self.winner!=self.old_winner:
                    #     #         line(p2,c,(80,80,80),9,color2=combine(self.input[self.old_winner].get_color(),(100,100,100),0.5),val=self.val)
                    #     #         line(p2,c,(100,100,100),color2=self.input[self.old_winner].get_color(),val=self.val)
                    #     #     else:
                    #     #         line(c,p2,(80,80,80),9)
                    #     #         line(c,p2,(100,100,100))
                    #     # else:
                    #     #     if self.winner!=self.old_winner:
                    #     #         col = (100,100,100)
                    #     #         if self.old_winner != -1:
                    #     #             col = self.input[self.old_winner].get_color()
                    #     #         line(c,p2,combine(b.get_color(),(100,100,100),0.5),9,color2=col,val=self.val)
                    #     #         line(c,p2,b.get_color(),color2=(100,100,100),val=self.val)
                    #     #     else:
                    #     #         line(c,p2,combine(b.get_color(),(100,100,100),0.5),9)
                    #     #         line(c,p2,b.get_color())
                    #     if self.winner==i and self.get_val()==b.get_val():
                    #         line(c,p2,combine(b.get_color(),(100,100,100),0.5),9)
                    #         # line(c,p2,(0,0,0),1)
                    #     else:
                    #         line(c,p2,combine(b.get_color(),(100,100,100),0.5),9)
                    #         line(c,p2,(0,0,0))
                        

                    # else:
                    #     if self.winner==i and self.get_val()==b.get_val():
                    #         line(c,p2,combine(b.get_color(),(0,0,0),0.2),9)
                    #     else:
                    #         line(c,p2,combine(b.get_color(),(0,0,0),0.2),9)
                    #         line(c,p2,(0,0,0))
                    i+=1
            
            image = Match_Base.copy()
            mask = Match_Mask.copy()
            
            # pygame.draw.rect(screen,combine(color,(100,100,100),0.5),[p[0]-22,p[1]-22,44,44],border_radius=7)
            # pygame.draw.rect(screen,color,[p[0]-20,p[1]-20,40,40],border_radius=5)
        else:
            
            image = Contestant_Base.copy()
            mask = Contestant_Mask.copy()
            # pygame.draw.circle(screen,combine(color,(100,100,100),0.6),p,24)
            # pygame.draw.circle(screen,color,p,20)
        if not (0<p[1]<screen.get_height()):
            return 
        if isinstance(self,Match):
            bool_v = False
            if not EditMode:
                if self == next_match:
                    if self.old_winner==self.winner:
                        bool_v = True
            
            self.next_match_anim_val = self.next_match_anim_val*0.8+bool_v*0.2
            if not bool_v and self.next_match_anim_val<0.1:
                self.render_time=-90*15
            if self.next_match_anim_val>0.1:
                v = (math.sin(self.render_time/15)*8+8)*self.next_match_anim_val
                image1 = pygame.transform.smoothscale(image.copy(),[x+v for x in image.get_size()])
                
                screen.blit(image1,Center(p,image1))
        
        
        a = pygame.Surface((48,48))
        a.fill(color)
        a.blit(mask,(0,0))
        a.set_colorkey(Mask_Color)
        a.set_alpha(140)
        image.blit(a,(0,0))
            # if self.out:
            #     a = Eliminated.copy()
            #     a.blit(mask,(0,0))
            #     a.set_colorkey(Mask_Color)
            #     a.set_alpha(Eliminated.get_alpha())
            #     image.blit(a,(0,0))
            # if dist(pygame.mouse.get_pos(),p)<25:
            #     a = Highlighted.copy()
            #     a.blit(mask,(0,0))
            #     a.set_colorkey(Mask_Color)
            #     a.set_alpha(Highlighted.get_alpha())
            #     image.blit(a,(0,0))
        screen.blit(image,Center(p,image))
        # if self==MovingBlock:
        #     pygame.draw.circle(screen,(255,0,0),p,30,width=5)
        # if self==SelectedBlock:
        #     pygame.draw.circle(screen,(0,255,0),p,30,width=5)
    

        if val!="":
            font = FontSmallBold
            if len(val)>15:
                font = FontTinyBold
            if not self.out or EditMode:
                Text(val,(50,50,50),p,font,PosType=(1,1),background=(154+color[0]*0.3,154+color[1]*0.3,154+color[2]*0.3,200))
            else:
                Text(val,(50,50,50),p,font,PosType=(1,1),background=(100+color[0]*0.4,100+color[1]*0.4,100+color[2]*0.4,200))
        self.render_time+=1
class Match(Block):
    def __init__(self, index, column, input):
        super().__init__(index, column, input)
        self.winner = -1
        self.old_winner = -1
        self.val = 0
        self.next_match_anim_val = 0
    def get_val(self):
        if self.winner!=-1:
            return self.input[self.winner].get_val()
        else:
            return ""
    def get_data(self):
        d = super().get_data()
        d["winner"] = self.winner
        return d
    
    
    
        
    
class Contestant(Block):
    def __init__(self, value,color, index, column):
        super().__init__(index, column, None)
        self.color = color
        self.value = value
    
    def get_val(self):
        return self.value
    def get_data(self):
        d = super().get_data()
        d["color"] = self.color
        d["value"] = self.value
        return d
   

class Button:
    def __init__(self,pos: list,image: pygame.Surface):
        self._pos = list(pos)
        self._image = image
        self._pressed = False
        self._pres = False
        self.isClicked = False
        self.isNotClicked = False
    def set_pos(self,pos):
        self._pos = list(pos)
    def draw(self,scr):
        image = self._image.copy()
        if self.get_hover() and not self.isNotClicked:
            i2 = pygame.Surface(image.get_size())
            if pygame.mouse.get_pressed()[0]:
                i2.fill((255,255,255))
                i2.set_alpha(80)
            else:
                i2.fill((100,150,255))
                i2.set_alpha(40)

            image.blit(i2,(0,0))
        scr.blit(image,[self._pos[0]-image.get_width()/2,self._pos[1]-image.get_height()/2])
    
    def tick(self,*args):
        global MouseOverButton
        mdown = pygame.mouse.get_pressed()[0]
        hov = self.get_hover()
        
        if hov and mdown and not self._pres:
            self.isClicked = True
        if (not hov):
            self.isNotClicked = True
        if self.isClicked and self._pres and not mdown and self.get_hover():
            self._pressed = True
            self.trigger(*args)
        self._pres = pygame.mouse.get_pressed()[0]
        if not mdown or not hov:
            self.isClicked = False
        if not mdown:
            self.isNotClicked = False
        if self.isClicked:
            MouseOverButton = True
    def get_hover(self):
        mx,my = pygame.mouse.get_pos()
        return (self._pos[0]-self._image.get_width()/2<mx<self._pos[0]+self._image.get_width()/2) and (self._pos[1]-self._image.get_height()/2<my<self._pos[1]+self._image.get_height()/2) 
    def trigger(self,*args):
        pass
class Blank(Block):
    def __init__(self, index, column):
        super().__init__(index, column, None)
    def update(self, events):
        return
    def render(self):
        return
    def get_data(self):
        return
class ColorSelector():
    def __init__(self,pos,colors,columns=5):
        def set_last_color(color,sel):
            sel.last_click_color = color
        self.pos = list(pos)
        self.colors = colors
        self.columns = columns
        self.pressed = False
        self.hover = False
        self.buttons = []
        self.size = 50
        self.border_size = 15
        self.last_click_color = colors[0]
        self.current_button = 0
        row = 0
        column = 0
        for c in colors:
            i = pygame.Surface((self.size*0.75,self.size*0.75))
            i.fill(Mask_Color)
            i.set_colorkey(Mask_Color)
            pygame.draw.rect(i,c,[0,0,self.size*0.75,self.size*0.75],border_radius=7)
            b = Button([self.pos[0]+(column-columns/2)*self.size,self.pos[1]+(row-math.floor(len(colors)/columns)/2)*self.size],i)
            b.trigger = set_last_color
            self.buttons.append(b)
            column+=1
            if column>=columns:
                row+=1
                column = 0
        
    def update(self):
        column = 0
        row = 0
        self.current_button = 0
        for b in self.buttons:
            b.set_pos([self.pos[0]+(column-self.columns/2)*self.size,self.pos[1]+(row-math.floor(len(self.colors)/self.columns)/2)*self.size])
            b.tick(self.colors[self.current_button],self)
            column+=1
            self.current_button+=1
            if column>=self.columns:
                column=0
                row+=1
                    
    def render(self,image):
        pos = [self.pos[0]-(self.columns/2)*self.size,self.pos[1]-(math.floor(len(self.colors)/self.columns)/2)*self.size]
        size = [self.columns*self.size,math.ceil(len(self.colors)/self.columns)*self.size]
        pygame.draw.rect(image,(70,70,70),[pos[0]-self.size/2-self.border_size/2,pos[1]-self.size/2-self.border_size/2,size[0]+self.border_size,size[1]+self.border_size],border_radius=18)
        column = 0
        row = 0
        for b in self.buttons:
            b.set_pos([self.pos[0]+(column-self.columns/2)*self.size,self.pos[1]+(row-math.floor(len(self.colors)/self.columns)/2)*self.size])
            b.draw(image)
            column+=1
            if column>=self.columns:
                column=0
                row+=1
            
contestants = 10
blocks = []
def gen_color(num):
    num%=1530
    r = 0
    g = 0
    b = 0
    if num<=255:
        r = 255
        g = num
    elif 255<=num<=510:
        r = 510-num
        g = 255
    elif 510<=num<=765:
        g = 255
        b = num-510
    elif 765<=num<=1020:
        b = 255
        g = 1020-num
    elif 1020<=num<=1275:
        b = 255
        r = num-1020
    elif 1275<=num<=1530:
        b = 1530-num
        r = 255
    
    return (r,g,b)
def get_val(index,names):
    if names!=None:
        return names[index]
    else:
        global contestant_names
        if len(contestant_names)-1<index:
            v = ""
        else:
            v = contestant_names[index].join(contestant_names[index].get_text())
    if v!="":
        return v
    else:
        return "Unnamed"
def reload_stats():
    total_contestants = contestants
    floor = math.floor(math.log2(total_contestants))
    pregame_matches = total_contestants%2**floor
    i = 2**floor-1
    total_matches = i+pregame_matches
    remaining_matches = i+pregame_matches
    completed_matches = 0
    recalculate_blocks()
def Setup(Contest,names=None):
    global contestants
    global blocks
    global contestant_names
    global remaining_contestants
    global remaining_matches
    global pregame_matches
    global next_match
    global eliminated_contestants
    global completed_matches
    global total_contestants
    global total_matches
    reset_stats()
    floor = math.floor(math.log2(Contest))
    blocks = [[] for x in range(floor+2)]
    contestants = Contest
    total_contestants = contestants
    remaining_contestants = contestants
    eliminated_contestants = 0
    pregames = Contest%(2**floor)
    pregame_matches = pregames
    index = 0
    for x in range(2**floor):
        if pregames>0:
            c1 = Contestant(get_val(index,names),gen_color(index*(1530/Contest)),x*2,0)
            c2 = Contestant(get_val(index+1,names),gen_color((index+1)*(1530/Contest)),x*2+1,0)
            c3 = Match(x,1,[c1,c2])
            if next_match==None:
                next_match = c3
            c1.set_output(c3)
            c2.set_output(c3)
            blocks[0].append(c1)
            blocks[0].append(c2)
            blocks[1].append(c3)
            pregames-=1
            index +=2
        else:
            c1 = Contestant(get_val(index,names),gen_color(index*(1530/Contest)),x,1)
            blocks[0].append(Blank(len(blocks[0]),0))
            blocks[0].append(Blank(len(blocks[0]),0))
            blocks[1].append(c1)
            index +=1
    i = 0
    for x in range(floor):
        for y in range(2**(floor-x-1)):
            c1 = blocks[x+1][y*2]
            c2 = blocks[x+1][y*2+1]
            c3 = Match(y,x+2,[c1,c2])
            if next_match==None:
                next_match = c3
            c1.set_output(c3)
            c2.set_output(c3)
            blocks[x+2].append(c3)
            i+=1
    total_matches = i+pregame_matches
    remaining_matches = i+pregame_matches
    completed_matches = 0
    render_ui()
    








def start():
    global MainMenu
    global CamX
    global CamY
    s = 0
    try:
        s = int(cont_box.join(cont_box.get_text()))


    except:
        set_error("Not A Number \""+cont_box.join(cont_box.get_text())+"\"")
        return
    if s < 2:
        set_error("Needs 2 or more contestants!")
        return
    Setup(s)
    MainMenu = False
    CamX = 0
    CamY = 0

def line(a:list,b:list,color,width=5,color2=None,val=1):
    dist = abs(a[0]-b[0])+abs(a[1]-b[1])
    x_dist = abs(a[0]-b[0])
    y_dist = abs(a[1]-b[1])
    #default
    if val>=1 or color2==None:
        pygame.draw.line(screen,color,a,[(a[0]+b[0])/2,a[1]],width)
        pygame.draw.circle(screen,color,[(a[0]+b[0])/2,a[1]],width*0.5)
        pygame.draw.line(screen,color,[(a[0]+b[0])/2,a[1]],[(a[0]+b[0])/2,b[1]],width)
        pygame.draw.circle(screen,color,[(a[0]+b[0])/2,b[1]],width*0.5)
        pygame.draw.line(screen,color,b,[(a[0]+b[0])/2,b[1]],width)
        return
    #completed
    if val<=0:
        pygame.draw.line(screen,color2,a,[(a[0]+b[0])/2,a[1]],width)
        pygame.draw.circle(screen,color2,[(a[0]+b[0])/2,a[1]],width*0.5)
        pygame.draw.line(screen,color2,[(a[0]+b[0])/2,a[1]],[(a[0]+b[0])/2,b[1]],width)
        pygame.draw.circle(screen,color2,[(a[0]+b[0])/2,b[1]],width*0.5)
        pygame.draw.line(screen,color2,b,[(a[0]+b[0])/2,b[1]],width)
        return
    #first horizontal
    if dist*val<x_dist/2:
        v = 1-(val)*(dist/(x_dist/2))
        pygame.draw.circle(screen,color2,[(a[0]+b[0])/2,a[1]],width*0.5)
        pygame.draw.line(screen,color,a,[(a[0]*v+((a[0]+b[0])/2)*(1-v)),a[1]],width)
        pygame.draw.line(screen,color2,[(a[0]+b[0])/2,a[1]],[(a[0]*v+((a[0]+b[0])/2)*(1-v)),a[1]],width)
    else:
        pygame.draw.circle(screen,color,[(a[0]+b[0])/2,a[1]],width*0.5)
        pygame.draw.line(screen,color,a,[(a[0]+b[0])/2,a[1]],width)
    #vertical
    if x_dist/2<dist*val<x_dist/2+y_dist:
        v = 1-(val-(x_dist/2)/dist)*((dist)/(y_dist))
        
        pygame.draw.circle(screen,color2,[(a[0]+b[0])/2,b[1]],width*0.5)
        pygame.draw.line(screen,color,[(a[0]+b[0])/2,a[1]],[(a[0]+b[0])/2,a[1]*v+b[1]*(1-v)],width)
        pygame.draw.line(screen,color2,[(a[0]+b[0])/2,b[1]],[(a[0]+b[0])/2,a[1]*v+b[1]*(1-v)],width)
    elif x_dist/2>=dist*val:
        pygame.draw.circle(screen,color2,[(a[0]+b[0])/2,b[1]],width*0.5)
        pygame.draw.line(screen,color2,[(a[0]+b[0])/2,a[1]],[(a[0]+b[0])/2,b[1]],width)
    else:
        pygame.draw.circle(screen,color,[(a[0]+b[0])/2,b[1]],width*0.5)
        pygame.draw.line(screen,color,[(a[0]+b[0])/2,a[1]],[(a[0]+b[0])/2,b[1]],width)
    #second horizontal
    if y_dist+x_dist/2<dist*val<dist:
        v = 1-(val-(x_dist/2+y_dist)/dist)*((dist)/(x_dist/2))
        
        pygame.draw.line(screen,color,[(a[0]+b[0])/2,b[1]],[((a[0]+b[0])/2)*v+b[0]*(1-v),b[1]],width)
        pygame.draw.line(screen,color2,b,[((a[0]+b[0])/2)*v+b[0]*(1-v),b[1]],width)
    elif dist*val<=y_dist+x_dist/2:
        pygame.draw.line(screen,color2,b,[(a[0]+b[0])/2,b[1]],width)
def calc_pos(x,y):
    if 2**(math.floor(math.log2(total_contestants)))==total_contestants:
        return [(x-1)*((screen.get_width()-scale_x(550))/(len(blocks)-2))+80,(y+0.5)*(2**(x)*50)+20-CamY]
    return [x*((screen.get_width()-scale_x(550))/(len(blocks)-1))+80,(y+0.5)*(2**(x)*50)+20-CamY]
def combine(a,b,val):
    return [a[0]*val+b[0]*(1-val),a[1]*val+b[1]*(1-val),a[2]*val+b[2]*(1-val)]
def toggle_edit():
    global EditMode
    EditMode = not EditMode

def scale_y(a):
    return (a/Info_Image.get_height())*Info_GUI.img.get_height()
def scale_x(a):
    return (a/Info_Image.get_width())*Info_GUI.img.get_width()

def render_ui():
    Info_GUI.render()
class Info_GUI_Class:
    def __init__(self):
        self.edit_button = Button([0,0],Edit_Image)
        self.edit_button.trigger = toggle_edit
        self.img = pygame.Surface((0,0))
        self.edit_anim_val = 0
        p = pygame.Surface([64,40])
        p.set_colorkey((0,0,0))
        Text("Save",(255,255,255),[x/2 for x in p.get_size()],FontMediumSmall,[1,1],(150,150,150),p)
        self.save_button = Button([0,0],p)
        self.save_button.trigger = lambda : save(self.file_box.join(self.file_box.get_text()))

        p = pygame.Surface([68,40])
        p.set_colorkey((0,0,0))
        Text("Load",(255,255,255),[x/2 for x in p.get_size()],FontMediumSmall,[1,1],(150,150,150),p)
        self.load_button = Button([0,0],p)
        self.load_button.trigger = lambda : load(self.file_box.join(self.file_box.get_text()))
        self.file_box = TextBox("File",0,0,None,[1,1],FontMediumSmall)

    def render(self):
        self.edit_anim_val = self.edit_anim_val*0.8+EditMode*0.2
        self.img = pygame.transform.smoothscale(Info_Image,(Info_Image.get_width()/Info_Image.get_height()*screen.get_height(),screen.get_height()))
        screen.blit(self.img,[screen.get_width()-self.img.get_width(),0])
        global scale
        scale = self.img.get_width()
        alpha = 120
        
        if not EditMode or self.edit_anim_val<0.99:
            pos_offset = (400*self.edit_anim_val,0)
            # pygame.draw.rect(screen,(80,80,80),[screen.get_width()-400,10,400,screen.get_height()-20],border_bottom_left_radius=50,border_top_left_radius=50)
            Text(" I N F O ",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(50)+pos_offset[1]),FontLargeNormalBold,(1,0),(120,120,120,alpha))
            Text("Matches",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(140)+pos_offset[1]),FontNormal,(1,0),(120,120,120,alpha))
            
            if next_match!=None:
                
                Text("Next:",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(190)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
                c = next_match.input[0].get_color()
                Text(next_match.input[0].get_val(),combine((255,255,255),c,0.6),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(220)+pos_offset[1]),FontSmall,(1,0),combine((120,120,120),c,0.7))
                Text("VS",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(250)+pos_offset[1]),FontSmall,(1,0),(120,120,120,alpha))
                c = next_match.input[1].get_color()
                Text(next_match.input[1].get_val(),combine((255,255,255),c,0.6),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(280)+pos_offset[1]),FontSmall,(1,0),combine((120,120,120),c,0.7))
            else:
                
                Text("Winner:",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(190)+pos_offset[1]),FontMediumSmallBold,(1,0),(120,120,120,alpha))
                c = blocks[len(blocks)-1][0].get_color()
                Text(blocks[len(blocks)-1][0].get_val(),combine((255,255,255),c,0.6),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(250)+pos_offset[1]),FontMediumSmall,(1,0),combine((120,120,120),c,0.7))
            Text("Remaining:",(255,255,255),(screen.get_width()-scale_x(260)+pos_offset[0],scale_y(330)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(remaining_matches),(255,255,255),(screen.get_width()-scale_x(260)+pos_offset[0],scale_y(360)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text("Completed:",(255,255,255),(screen.get_width()-scale_x(140)+pos_offset[0],scale_y(330)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(completed_matches),(255,255,255),(screen.get_width()-scale_x(140)+pos_offset[0],scale_y(360)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text("Total:",(255,255,255),(screen.get_width()-scale_x(260)+pos_offset[0],scale_y(400)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(total_matches),(255,255,255),(screen.get_width()-scale_x(260)+pos_offset[0],scale_y(430)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text("Pregame:",(255,255,255),(screen.get_width()-scale_x(140)+pos_offset[0],scale_y(400)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(pregame_matches),(255,255,255),(screen.get_width()-scale_x(140)+pos_offset[0],scale_y(430)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text("Contestants",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(480)+pos_offset[1]),FontNormal,(1,0),(120,120,120,alpha))
            Text("Remaining:",(255,255,255),(screen.get_width()-scale_x(300)+pos_offset[0],scale_y(540)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(remaining_contestants),(255,255,255),(screen.get_width()-scale_x(300)+pos_offset[0],scale_y(570)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text("Eliminated:",(255,255,255),(screen.get_width()-scale_x(100)+pos_offset[0],scale_y(540)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(eliminated_contestants),(255,255,255),(screen.get_width()-scale_x(100)+pos_offset[0],scale_y(570)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text("Total:",(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(540)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
            Text(str(total_contestants),(255,255,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(570)+pos_offset[1]),FontSmallBold,(1,0),(120,120,120,alpha))
        if EditMode or self.edit_anim_val>0.01:
            pos_offset = (400*(1-self.edit_anim_val),0)
            Text(" E D I T ",(200,200,255),(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(50)+pos_offset[1]),FontLargeNormalBold,(1,0),(80,80,120,alpha))
            self.save_button.set_pos((screen.get_width()-scale_x(160)+pos_offset[0],scale_y(230)+pos_offset[1]))
            self.save_button.draw(screen)
            self.save_button.tick()
            self.load_button.set_pos((screen.get_width()-scale_x(240)+pos_offset[0],scale_y(230)+pos_offset[1]))
            self.load_button.draw(screen)
            self.load_button.tick()
            self.file_box.screen=screen
            self.file_box.setPos(screen.get_width()-scale_x(200)+pos_offset[0],scale_y(180)+pos_offset[1])
            self.file_box.update(events)
        
        
        
        self.edit_button.set_pos((screen.get_width()-scale_x(200),scale_y(700)))
        if SelectedBlock == None and TimeSinceSelected==0:
            self.edit_button.tick()
        self.edit_button.draw(screen)
Info_GUI = Info_GUI_Class()
def Center(a,image):
    return [a[0]-image.get_width()/2,a[1]-image.get_height()/2]
def Modify_Scroll_Y(val):
    global scroll_y
    scroll_y += val
    if MainMenu:
        if scroll_y>len(contestant_names)*90+60-screen.get_height():
            scroll_y=len(contestant_names)*90+60-screen.get_height()
        if scroll_y<0:
            scroll_y=0
    else:
        if scroll_y>calc_pos(1,len(blocks[1])-1)[1]-screen.get_height()+50+CamY:
            scroll_y=calc_pos(1,len(blocks[1])-1)[1]-screen.get_height()+50+CamY
        if scroll_y<0:
            scroll_y=0

def render_error():
    global Error_Time
    if Error_Time>0:
        Text("Error: "+Error,(255,0,0,min(255,Error_Time*20)),[screen.get_width()/2,screen.get_height()*0.9],FontNormalBold,[1,1],(100,0,0,min(255,Error_Time*20)))
        Error_Time-=1




def set_error(error,time=50):
    global Error
    global Error_Time
    Error = error
    Error_Time = time



def CloseSelectedGUI():
    global SelectedBlock
    global TimeSinceSelected
    TimeSinceSelected = screen.get_width()/30
    
    SelectedBlock = None
def SaveSelectedGUI():
    global SelectedBlock
    SelectedBlock.color = ColorSelect.last_click_color
    SelectedBlock.value = SelectedNameBox.join(SelectedNameBox.get_text())
    CloseSelectedGUI()

CancelSelectedButton = Button([0,0],pygame.image.load("Cancel.png"))
CancelSelectedButton.trigger = CloseSelectedGUI
SaveSelectedButton = Button([0,0],pygame.image.load("Save.png"))
SaveSelectedButton.trigger = SaveSelectedGUI
SelectedNameBox = TextBox("Contestant Name:",0,0,None,[0,0],FontNormal)
SelectedNameBox.Max_Lines = 1
SelectedBlockText = ""
SelectedBlockColor = (0,0,0)
ColorSelect = ColorSelector([0,0],[(255,255,255),
                                   (255,0,0),
                                   (0,255,0),
                                   (0,0,255),
                                   (0,0,0)])
def regenerateColorSelect():
    global ColorSelect
    l = [SelectedBlockColor]
    [l.append(gen_color(x)) for x in range(0,1520,64)]
    [l.append([x,x,x]) for x in range(0,255,51)]

    ColorSelect = ColorSelector([0,0],l,10)

def Selected_GUI():
    global SelectedBlock
    if TimeSinceSelected>0 or SelectedBlock!=None:
        if not isinstance(SelectedBlock,Contestant) and SelectedBlock!=None:
            CloseSelectedGUI()
            return
        image = pygame.Surface(screen.get_size())
        image.fill(Mask_Color)
        image.set_colorkey(Mask_Color)
        size = min(TimeSinceSelected*30,image.get_width()*0.8)
        pygame.draw.rect(image,combine((50,50,50),SelectedBlockColor,0.95),[image.get_width()/2-size/2,image.get_height()*0.1,size,image.get_height()*0.8],border_radius=30)
        # image.fill(combine((50,50,50),SelectedBlock.get_color(),0.95))
        
        
        
        Text("Modifying \""+SelectedBlockText+"\"",combine((255,255,255),SelectedBlockColor ,0.7),(image.get_width()*0.5,image.get_height()*0.2),FontMediumLargeBold,[1,0],scr=image)
        SelectedNameBox.screen=image
        SelectedNameBox.setPos(image.get_width()*0.1+30,image.get_height()*0.4)
        SelectedNameBox.update(events)
        ColorSelect.pos = [image.get_width()*0.37,image.get_height()*0.7]
        ColorSelect.update()
        ColorSelect.render(image)
        pygame.draw.circle(image,ColorSelect.last_click_color,[image.get_width()*0.7,image.get_height()*0.67],40)
        Text("Color",(255,255,255),[image.get_width()*0.7,image.get_height()*0.67],FontNormalBold,[1,1],(200,200,200,200),image)

        CancelSelectedButton.set_pos((image.get_width()*0.9-220,image.get_height()*0.9-60))
        if SelectedBlock!=None:
            CancelSelectedButton.tick()
        CancelSelectedButton.draw(image)
        SaveSelectedButton.set_pos((image.get_width()*0.9-90,image.get_height()*0.9-60))
        if SelectedBlock!=None:
            SaveSelectedButton.tick()
        SaveSelectedButton.draw(image)
        image2 = pygame.Surface((size,image.get_height()))
        image2.fill(Mask_Color)
        image2.set_colorkey(Mask_Color)
        image2.blit(image,(-image.get_width()/2+image2.get_width()/2,0))
        screen.blit(image2,Center([x/2 for x in screen.get_size()],image2))

def move_block():
    global MovingBlock
    global blocks
    if not pygame.mouse.get_pressed()[0]:
        MovingBlock = None
        # pygame.draw.circle(screen,(0,0,255),pygame.mouse.get_pos(),10)
        return
    next_block = None
    min_dist = 100
    mx,my = pygame.mouse.get_pos()
    
    for x in blocks[MovingBlock.column]:
        d = dist(calc_pos(x.column,x.index),(mx,my))
        if d<min_dist:
            min_dist = d
            next_block = x
        
    if next_block == None:
        return
    pos = calc_pos(next_block.column,next_block.index)
    # pygame.draw.rect(screen,(255,255,0),[pos[0]-25,pos[1]-25,50,50],3)
    
    for a in range(MovingBlock.column+1):
        column_diff = MovingBlock.column-a
        alt_index_start = next_block.index*(2**column_diff)
        alt_index_end = alt_index_start+(2**column_diff)-1
        index_start = MovingBlock.index*(2**column_diff)
        index_end = index_start+(2**column_diff)-1
        move_blocks = []
        # pygame.draw.circle(screen,(255,0,0),calc_pos(a,index_start),20)
        # Text(str(index_start),(255,255,255),calc_pos(a,index_start),FontTiny,[1,1])
        # pygame.draw.circle(screen,(255,0,0),calc_pos(a,index_end),20)
        # Text(str(index_end),(255,255,255),calc_pos(a,index_end),FontTiny,[1,1])
        # pygame.draw.circle(screen,(255,0,0),calc_pos(a,alt_index_start),20)
        # Text(str(alt_index_start),(255,255,255),calc_pos(a,alt_index_start),FontTiny,[1,1])
        # pygame.draw.circle(screen,(255,0,0),calc_pos(a,alt_index_end),20)
        # Text(str(alt_index_end),(255,255,255),calc_pos(a,alt_index_end),FontTiny,[1,1])
        if a==0 and column_diff==0:
            stop = False
            for b in range(max(index_start,index_end,alt_index_start,alt_index_end)-min(index_start,index_end,alt_index_start,alt_index_end)+1):
                c = b+min(index_start,index_end,alt_index_start,alt_index_end)
                # pygame.draw.circle(screen,(255,255,255),calc_pos(a,c),10)
                if isinstance(blocks[a][c],Blank):
                    stop = True
                    break
            if stop:
                return
        for b in range(index_end-index_start+1):
            c = b+index_start
            move_blocks.append(blocks[a][c])
        for b in range(index_end-index_start+1):
            c = b+index_start
            block = move_blocks[b]
            
            
            # pygame.draw.circle(screen,(255,0,0),calc_pos(a,c),20)
            # Text(str(c),(255,255,255),calc_pos(a,c),FontTiny,[1,1])
            

            c2 = (alt_index_start+b if index_end>alt_index_end else alt_index_end)
            blocks[a].remove(block)
            
            # pygame.draw.circle(screen,(255,255,0),[calc_pos(a,c)[0]-10,calc_pos(a,c)[1]],20)
            # Text(str(c),(0,0,0),calc_pos(a,c),FontTiny,[1,1])
            blocks[a].insert(c2,block)
    recalculate_blocks()
            
            
        
    
def recalculate_blocks():
    global blocks
    for a in range(len(blocks)):
        for b in range(len(blocks[a])):
            if blocks[a][b]!=-1:
                blocks[a][b].column = a
                blocks[a][b].index = b
                if isinstance(blocks[a][b],Match):
                    blocks[a][b].input = [blocks[a-1][b*2],blocks[a-1][b*2+1]]
                    blocks[a-1][b*2].output = blocks[a][b]
                    blocks[a-1][b*2+1].output = blocks[a][b]
                else:
                    if a>0:
                        blocks[a-1][b*2].output = blocks[a][b]
                        blocks[a-1][b*2+1].output = blocks[a][b]
                    

screen = pygame.display.set_mode((1200,800),pygame.RESIZABLE)
clock = pygame.time.Clock()
scale = 600
running = True
cont_box =TextBox("Contestants",screen.get_width()/2,screen.get_height()/2,screen,[1,0],FontNormal,True)
button = Button((screen.get_width()/2,screen.get_height()/2+140),pygame.image.load("Generate.png"))
button.trigger = start
background_real = pygame.image.load("background.png")
scroll_y = 0
Logo = pygame.image.load("TournamentG.png")

while running:
    screen.fill((0,0,0))
    background = pygame.transform.smoothscale(background_real,screen.get_size())
    screen.blit(background,(0,0))
    events = []
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_TAB:
                save("robin")
            if event.key == pygame.K_LALT:
                load("robin")
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            Modify_Scroll_Y(-event.y*50)
        else:
            events.append(event)
    mx,my = pygame.mouse.get_pos()

    if my<50:
        Modify_Scroll_Y(-10)
    if my>screen.get_height()-50:
        Modify_Scroll_Y(10)
    CamY += (scroll_y-CamY)/10
    if MainMenu:
        cont_box.setPos(screen.get_width()/2,screen.get_height()/2)
        button.set_pos((screen.get_width()/2,screen.get_height()/2+140))
        screen.blit(Logo,Center((screen.get_width()/2,150),Logo))
        cont_box.update(events)
        button.tick()
        button.draw(screen)
        a = False
        try:
            i = int(cont_box.join(cont_box.get_text()))
            a = True
        except:
            pass
        if a:
            
            l = len(contestant_names)
            while l!=i:
                if l>i:
                    contestant_names.pop()
                elif l<i:
                    t = TextBox("Contestant #"+str(l+1),0,0,screen,[-1,0],FontNormal)
                    t.Max_Lines=1
                    contestant_names.append(t)
                l = len(contestant_names)
            
        index = 0
        for c in contestant_names:
            c.Pos = (screen.get_width()-20,90*index+60-CamY)
            c.update(events)
            index+=1
    else:
        blocks2 = blocks.copy()
        blocks2.reverse()
        for column in blocks2:
            for block in column:
                if block!=-1:
                    block.update(events)
                    block.render()
        render_ui()
        
        if EditMode:
            if SelectedBlock != None:
                if TimeSinceSelected<0:
                    TimeSinceSelected = 0
                if TimeSinceSelected==0:
                    SelectedNameBox.set_text(SelectedBlock.get_val())
                    SelectedBlockText = SelectedBlock.get_val()
                    SelectedBlockColor = SelectedBlock.get_color()
                    regenerateColorSelect()
                TimeSinceSelected+=1
            else:
                if TimeSinceSelected>0:
                    TimeSinceSelected -= 1
            Selected_GUI()
            if MovingBlock != None:
                move_block()
    render_error()
    pygame.display.update()
    clock.tick(60)
pygame.quit()