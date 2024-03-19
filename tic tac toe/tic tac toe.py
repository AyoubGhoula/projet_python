from tkinter import*
import random
def rest():
    global turn
    for i in range(3):
        for j in range(3):
            game_btn[i][j]['text']=""
    label.config(text=(turn+" player"))

def next_turn(row,col):
    global turn,players,o_win,x_win
    if game_btn[row][col]['text']=="" and check_win()==False:
        game_btn[row][col]['text']=turn
        if check_win()==False:
            if turn==players[0]:
                turn=players[1]
                label.config(text=(turn+" player"))
            else:
                turn=players[0]
                label.config(text=(turn+" player"))
        elif check_win()==True:
            label.config(text=(turn+" win"))
            if turn=='o':
                o_win+=1
            else:
                x_win+=1
            x.config(text=("x="+str(x_win)))
            o.config(text=("o="+str(o_win)))
        else:
            label.config(text=("no win"))
            
            
def check_win():
    b=game_btn
    for i in range(3):
        if b[i][0]['text']!="":
            if b[i][0]['text']==b[i][1]['text'] and b[i][0]['text']==b[i][2]['text']:
                return True
    for i in range(3):
        if b[0][i]['text']!="":
            if b[0][i]['text']==b[1][i]['text'] and b[0][i]['text']==b[2][i]['text']:
                return True
    if b[0][0]['text']!="":
        if b[0][0]['text']==b[1][1]['text'] and b[0][0]['text']==b[2][2]['text']:
            return True
    if b[0][2]['text']!="":
        if b[0][2]['text']==b[1][1]['text'] and b[0][2]['text']==b[2][0]['text']:
            return True
    v=True
    for i in range(3):
        for j in range(3):
            if b[i][j]['text']=="":
                v=False
                break
    if v==True:
        return "no win"
    return False
window=Tk()
window.title("Tic-Tac-Toe")

players=['x','o']
turn=random.choice(players)
x_win=0
x=Label(text=("x="+str(x_win)),font=('consolas',40))
x.pack(side='left')
o_win=0
o=Label(text=("o="+str(o_win)),font=('consolas',40))
o.pack(side='left')
label=Label(text=(turn+" player"),font=('consolas',40))
label.pack(side='top')
restart=Button(text="restart",font=('consolas',20),command=rest)
restart.pack(side='top')
frame=Frame(window)
frame.pack()
game_btn=[
    [0,0,0],
    [0,0,0],
    [0,0,0]]
for i in range(3):
    for j in range(3):
        game_btn[i][j]=Button(frame,text="",font=('consolas',40),width=4,height=1,command=lambda row=i,col=j:next_turn(row,col))
        game_btn[i][j].grid(row=i,column=j)
   
window.mainloop()