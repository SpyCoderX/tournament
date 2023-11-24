import pygame
pygame.init()
pygame.font.init()
class TextBox:
    def __init__(self,Name="TextBox",x=0,y=0,screen=pygame.Surface((10,10)),PosType=[0,0],font=None,numbers_only=False):
        self._listOfKeysPressed = []
        self.Word = [[]]
        self._Cursor_X = 0
        self._Cursor_Y = 0
        self.screen = screen
        self.Name = Name
        self.PosType = PosType
        self.Pos = (x,y)
        self._HeldKey = ["",0]
        self._Cursor_Bool = True
        self._Selected = False
        self._check_selected = False
        self._number_mode = numbers_only
        self._Cursor_Time = 0
        self.Max_Letters = 100
        self.Max_Lines = 10
        self.ShiftDiction = {"[":"{","]":"}","-":"_","=":"+",
                        "1":"!","2":"@","3":"#","4":"$",
                        "5":"%","6":"^","7":"&","8":"*",
                        "9":"(","0":")","/":"?",".":">",
                        ",":"<","'":'"',"`":"~","\\":"|"}
        self.AllowedLetters = ["a","b","c","d","e","f","g","h","i","j","k","l","m",
                          "n","o","p","q","r","s","t","u","v","w","x","y","z",
                          "0","1","2","3","4","5","6","7","8","9","[","]","-",
                          "=",";","'",",",".","/","return","delete","backspace","tab","`","left","up","down","right","space"]
        self.Numbers = ["0","1","2","3","4","5","6","7","8","9"]
        self.AllowedNumbers = [92]
        if font != None:
            self.Font = font
        else:
            self.Font = pygame.font.SysFont("Arial", 20)
        self._LShift = False
        self._RShift = False

    def Text(self,ttext = "",color = (255,255,255),pos = (0,0),font = pygame.font,PosType = (1,0)):
        text = font.render(ttext, True, color)
        if len(color) > 3:
            text.set_alpha(color[3])
        text_rect = text.get_rect()
        if PosType[0] == 0:
            text_rect.x = pos[0]
        elif PosType[0] == 1:
            text_rect.centerx = pos[0]
        elif self.PosType[0] == -1:
            text_rect.x = pos[0]-text_rect.w
        if PosType[1] == 0:
            text_rect.y = pos[1]
        elif PosType[1] == 1:
            text_rect.centery = pos[1]

        self.screen.blit (text, text_rect)

    def get_rect_of_text(self,text='',font=pygame.font):
        text = font.render(text,True,(0,0,0))
        text_rect = text.get_rect()
        return text_rect

    def join(self,List):
        word = ""
        for section in List:
            for item in section:
                for letter in item:
                    word = word + str(letter)
        return str(word)

    def unjoin(self,Word):
        List = [[]]
        index = 0
        for item in Word:
            for letter in item:
                if letter == "\n":
                    index += 1

                List[index].append(str(letter))
        return List

    def event(self,events):
        for event in events:
            print(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    self.LShift = True
                    continue
                if event.key == pygame.K_RSHIFT:
                    self.RShift = True
                    continue
                key = pygame.key.name(event.key)
                if self._number_mode:
                    try:
                        self.Numbers.index(key)
                    except ValueError:
                        continue
                else:
                    try:
                        self.AllowedLetters.index(key)
                    except ValueError:
                        try:
                            self.AllowedNumbers.index(pygame.key.key_code(key))
                        except ValueError:
                            continue
                self.HeldKey[0] = key
                if self.LShift or self.RShift and not self._number_mode:
                    new_key = key.upper()
                    if new_key == key:
                        try:
                            new_key = self.ShiftDiction[key]
                        except:
                            pass
                        finally:
                            key = new_key
                    else:
                            key = new_key

                self.listOfKeysPressed.append(key)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    self.LShift = False
                    continue
                if event.key == pygame.K_RSHIFT:
                    self.RShift = False
                    continue
                if pygame.key.name(event.key) == self.HeldKey[0]:
                    self.HeldKey[0] = ""
            if self.HeldKey[0] != "":
                self.HeldKey[1] += 1
            else:
                self.HeldKey[1] = 0
            if self.HeldKey[1] > 60:
                if self.HeldKey[1]%4 == 0:
                    self.listOfKeysPressed.append(self.HeldKey[0])


    def get_text(self):
        return self.Word
    def set_text(self,word):
        if type(word) == str:
            self.Word = self.unjoin(word)
        elif type(word) == list:
            self.Word = word
        elif type(word) == tuple:
            self.Word = list(word)
        else:
            raise ValueError("{0} is not an accepted input!".format(word))

    def maximum(self,List):
        Max = 0
        Item = ''
        for i in List:
            if len(i) > Max:
                Max = len(i)
                Item = i
        return Item
    def maximum_font(self,List,Font):
        Max = 0
        Item = ''
        for i in List:
            if self.get_rect_of_text(i,Font).width > Max:
                Max = self.get_rect_of_text(i,Font).width
                Item = i
        return Item
    def length(self,List):
        value = 0
        for section in List:
            value += len(section)
        return value
    def count(self,List,item):
        value = 0
        for section in List:
            value += section.count(item)
        return value
    def update(self,events):
        global ScreenWidth
        global ScreenHeight
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    self._LShift = True
                    continue
                if event.key == pygame.K_RSHIFT:
                    self._RShift = True
                    continue
                key = pygame.key.name(event.key)
                try:
                    self.AllowedLetters.index(key)
                except:
                    try:
                        self.AllowedNumbers.index(pygame.key.key_code(key))
                    except:
                        continue
                self._HeldKey[0] = key
                if self._LShift or self._RShift:
                    new_key = key.upper()
                    if new_key == key:
                        try:
                            new_key = self.ShiftDiction[key]
                        except:
                            pass
                        finally:
                            key = new_key
                    else:
                        key = new_key

                self._listOfKeysPressed.append(key)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    self._LShift = False
                    continue
                if event.key == pygame.K_RSHIFT:
                    self._RShift = False
                    continue
                if pygame.key.name(event.key) == self._HeldKey[0]:
                    self._HeldKey[0] = ""
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._check_selected = pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]

        if self._HeldKey[0] != "":
            self._HeldKey[1] += 1
        else:
            self._HeldKey[1] = 0
        if self._HeldKey[1] > 30:
            if self._HeldKey[1]%4 == 0:
                if self._LShift or self._RShift:
                    self._listOfKeysPressed.append(self._HeldKey[0].upper())
                else:
                    self._listOfKeysPressed.append(self._HeldKey[0])
        if self._Selected:
            for item in self._listOfKeysPressed:
                
                if item.lower() == "backspace":
                    try:
                        if self._Cursor_X-1 > -1:
                            i = self.Word[self._Cursor_Y][self._Cursor_X-1]
                            self.Word[self._Cursor_Y].pop(self._Cursor_X-1)
                            if i == "\n":
                                self.Word.pop(self._Cursor_Y)
                                self._Cursor_Y -= 1
                                self._Cursor_X = len(self.Word[self._Cursor_Y])
                    except:
                        pass
                    continue
                if item.lower() == "delete":
                    try:
                        self.Word[self._Cursor_Y].pop(self._Cursor_X)
                    except:
                        pass
                    continue
                if item.lower() == "left":
                    self._Cursor_X -= 1
                    continue
                if item.lower() == "right":
                    self._Cursor_X += 1
                    continue
                if item.lower() == "up":
                    self._Cursor_Y -= 1
                    continue
                if item.lower() == "down":
                    self._Cursor_Y += 1
                    continue
                if self.length(self.Word) >= self.Max_Letters:
                    break
                if self._number_mode:
                    try:
                        self.Numbers.index(item)
                    except:
                        continue
                if item.lower() == "return":
                    if len(self.Word) < self.Max_Lines:
                        self.Word.append([])
                        self._Cursor_Y += 1
                        self.Word[self._Cursor_Y].insert(self._Cursor_X,"\n")
                        self._Cursor_X = 1
                    continue
                if item.lower() == "space":
                    self.Word[self._Cursor_Y].insert(self._Cursor_X," ")
                    self._Cursor_X += 1
                    continue
                if item.lower() == "tab":
                    self.Word[self._Cursor_Y].insert(self._Cursor_X,"      ")
                    self._Cursor_X += 1
                    continue


                self.Word[self._Cursor_Y].insert(self._Cursor_X,item)
                self._Cursor_X += 1
        if self._Cursor_Y < 0:
            self._Cursor_Y = 0
        if self._Cursor_Y >= len(self.Word)-1:
            self._Cursor_Y = len(self.Word)-1
        if self._Cursor_X < 0:
            self._Cursor_X = 0
        if self._Cursor_X >= len(self.Word[self._Cursor_Y]):
            self._Cursor_X = len(self.Word[self._Cursor_Y])

        ReText = self.join(["=",self.maximum_font(self.join(self.Word).rsplit("\n"),self.Font),"="])
        text_box_rect = self.get_rect_of_text(ReText,self.Font)
        if self.PosType[0] == 0:
            text_box_rect.x = self.Pos[0]
        if self.PosType[1] == 0:
            text_box_rect.y = self.Pos[1]
        if self.PosType[0] == 1:
            text_box_rect.centerx = self.Pos[0]
        if self.PosType[1] == 1:
            text_box_rect.centery = self.Pos[1]
        if self.PosType[0] == -1:
            text_box_rect.x = self.Pos[0]-text_box_rect.w
        mx,my = pygame.mouse.get_pos()
        tbr = text_box_rect
        if self._check_selected:

            if tbr.left < mx < tbr.right and tbr.top < my < tbr.bottom:
                self._Selected = True
                self._Cursor_Y = len(self.Word)-1
                self._Cursor_X = len(self.Word[self._Cursor_Y])
            else:
                self._Selected = False
            self._check_selected = False
        if self._Selected:
            pygame.draw.rect(self.screen,(100,100,100), [text_box_rect.x-2.5,text_box_rect.y-2.5,text_box_rect.width+5,5+(len(self.Word)*text_box_rect.height)],border_radius=8)
        else:
            pygame.draw.rect(self.screen,(80,80,80), [text_box_rect.x-2.5,text_box_rect.y-2.5,text_box_rect.width+5,5+(len(self.Word)*text_box_rect.height)],border_radius=8)
        if tbr.left < mx < tbr.right and tbr.top < my < tbr.bottom and not self._Selected:
            pygame.draw.rect(self.screen,(150,150,150), [text_box_rect.x-2.5,text_box_rect.y-2.5,text_box_rect.width+5,5+(len(self.Word)*text_box_rect.height)],border_radius=8)
        if self._Selected:
            pygame.draw.rect(self.screen,(50,50,50), [text_box_rect.x,text_box_rect.y,text_box_rect.width,(len(self.Word)*text_box_rect.height)],border_radius=8)
            pygame.draw.rect(self.screen,(75,75,75), [text_box_rect.x,text_box_rect.y,text_box_rect.width-2,(-2)+(len(self.Word)*text_box_rect.height)],border_radius=8)
        else:
            pygame.draw.rect(self.screen,(30,30,30), [text_box_rect.x,text_box_rect.y,text_box_rect.width,(len(self.Word)*text_box_rect.height)],border_radius=8)
            pygame.draw.rect(self.screen,(60,60,60), [text_box_rect.x,text_box_rect.y,text_box_rect.width-2,(-2)+(len(self.Word)*text_box_rect.height)],border_radius=8)
        _Texts = self.join(self.Word).rsplit("\n")
        ReText = self.join(["=",self.maximum_font(_Texts,self.Font),"="])
        text_box_rect = self.get_rect_of_text(ReText,self.Font)
        if self.PosType[0] == 0:
            text_box_rect.x = self.Pos[0]
        if self.PosType[1] == 0:
            text_box_rect.y = self.Pos[1]
        if self.PosType[0] == 1:
            text_box_rect.centerx = self.Pos[0]
        if self.PosType[1] == 1:
            text_box_rect.centery = self.Pos[1]
        if self.PosType[0] == -1:
            text_box_rect.x = self.Pos[0]-text_box_rect.w
        TBR = text_box_rect
        _Texts = self.join(self.Word).rsplit("\n")
        i = 0
        for t in _Texts:
            for j in t:
                self.Text("  " + t,(255,255,255),(TBR.x,TBR.centery + (TBR.height*i)),self.Font,(0,1))
            i += 1
        if self._Cursor_Bool and self._Selected:
            word = ""
            depth = 0
            Lines = 0
            for letter in self.Word[self._Cursor_Y]:
                if depth == self._Cursor_X:
                    break
                if letter == "\n":
                    word = ''
                    depth += 1
                    Lines += 1
                    continue
                word = word + letter
                depth += 1
            Cursor_text_box = self.get_rect_of_text(word,self.Font)
            Cursor_text_box.x = text_box_rect.x+10
            if self.PosType[1] == 0:
                Cursor_text_box.centery = self.Pos[1]+Cursor_text_box.height/2
            if self.PosType[1] == 1:
                Cursor_text_box.centery = self.Pos[1]
            self.Text('|',(255,255,255),(Cursor_text_box.x+Cursor_text_box.width,Cursor_text_box.centery+(self._Cursor_Y*text_box_rect.height)),self.Font,(0,1))
            #pygame.draw.rect(self.screen,(255,255,255),((Cursor_text_box.x+Cursor_text_box.width,Cursor_text_box.y),(2,Cursor_text_box.height)))
        #self.Text("Word:" + str(self.Word),(255,255,255),(0,0),self.Font,(0,0))
        if self._Cursor_Time < 30:
            self._Cursor_Bool = True
        else:
            self._Cursor_Bool = False
        if self._Cursor_Time < 60:
            self._Cursor_Time += 1
        else:
            self._Cursor_Time = 0
        self._listOfKeysPressed = []
        index = 0
        for section in self.Word:
            try:
                section[0]
            except:
                if not index == 0:
                    self.Word.pop(index)
            index += 1
        
        self.Text(self.Name,(127,127,127),(self.Pos[0],self.Pos[1]-self.Font.get_height()*1.3),pygame.font.SysFont("Arial", self.Font.get_height()),self.PosType)
    def setName(self,name):
        self.Name = name
    def setPos(self,x,y):
        self.Pos = [x,y]
if __name__ == "__main__":
    screen = pygame.display.set_mode((1200,800))
    Textbox = TextBox("Box",600,400,screen,(1,1))
    keep_going = True
    clock = pygame.time.Clock()

    while keep_going:
       events = list(pygame.event.get())
       for event in events:
           if event.type == pygame.QUIT:
               keep_going = False
               break
       screen.fill((0,0,0))
       Textbox.update(events)
       pygame.display.update()
       clock.tick(60)
    pygame.quit()
