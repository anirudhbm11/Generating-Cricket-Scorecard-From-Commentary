import re
import pdb
import math
from tkinter import *

scores = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6}
batting_team = {}
bowling_team = {}
extras = {'b':0,'lb':0,'w':0,'nb':0}

def getting_out(line,batsmen,bowler):
    if batsmen not in batting_team:
        batting_team[batsmen] = {'status':'not out','R':0,'B':0,'4s':0,'6s':0,'SR':0.0}
    if bowler not in bowling_team:
        bowling_team[bowler] = {'O':0,'M':0,'R':0,'W':0,'NB':0,'WD':0,'ECO':0.0}
    wicket = ''
    if 'caught by' in line.lower():
        wicket = re.search(batsmen+r' c (.*?) b\s+'+bowler,line).group(1)
        batting_team[batsmen]['status'] = 'c '+wicket+' b '+bowler
        bowling_team[bowler]['W'] += 1
    if re.match(r'(.*?) to (.*?),\s*out bowled',line.lower()):
        wicket = bowler
        batting_team[batsmen]['status'] = 'b '+bowler
        bowling_team[bowler]['W'] += 1
    batting_team[batsmen]['B'] += 1

def addingBatsmenData(data,lines,runs):
    if data.group(2) not in batting_team:
        batting_team[data.group(2)] = {'status':'not out','R':0,'B':0,'4s':0,'6s':0,'SR':0.0}
    if runs == 0:
        pass
    if runs == 4:
        batting_team[data.group(2)]['R'] += int(runs)
        batting_team[data.group(2)]['4s'] += 1
    elif runs == 6:
        batting_team[data.group(2)]['R'] += int(runs)
        batting_team[data.group(2)]['6s'] += 1
    else:
        batting_team[data.group(2)]['R'] += int(runs)
    batting_team[data.group(2)]['B'] += 1


def addingExtras(data,lines,temp):
    if data.group(2) not in batting_team:
        batting_team[data.group(2)] = {'status':'not out','R':0,'B':0,'4s':0,'6s':0,'SR':0.0}
    if 'no run' in temp:
        converted_run = 0
    elif re.match('\d+',temp.split('|')[1]):
        converted_run = int(re.search('\d+',temp.split('|')[1]).group())
    else:
        converted_run = int(scores[temp.split('|')[1].lower()])
    if 'leg byes' in temp:
        extras['lb'] += int(converted_run)
        batting_team[data.group(2)]['B'] += 1
    elif 'byes' in temp:
        extras['b'] += int(converted_run)
        batting_team[data.group(2)]['B'] += 1  
    elif 'no ball' in temp:
        extras['nb'] += int(converted_run)
    elif temp == 'wide':
        extras['w'] += 1
    
def start():
    current_over_runs = 0
    with open('Data.txt','r') as f:
        for lines in reversed(f.readlines()):
            # pdb.set_trace()
            data = re.match(r'(.*?) to (.*?),\s*(.*?),',lines)
            if data:
                if 'out' in data.group(3).lower():
                    runs = 0
                    getting_out(lines,data.group(2),data.group(1))
                elif 'leg byes' in data.group(3).lower():
                    runs = 0
                    lbdata = re.match(r'(.*?) to (.*?),\s*(.*?),\s*(.*?),',lines)
                    addingExtras(data,lines,lbdata.group(3)+'|'+lbdata.group(4))
                elif 'byes' in data.group(3).lower():
                    runs = 0
                    bdata = re.match(r'(.*?) to (.*?),\s*(.*?),\s*(.*?),',lines)
                    addingExtras(data,lines,bdata.group(3)+'|'+bdata.group(4))
                elif 'wide' in data.group(3).lower():
                    if data.group(1) not in bowling_team:
                        bowling_team[data.group(1)] = {'O':0,'M':0,'R':0,'W':0,'NB':0,'WD':0,'ECO':0.0}
                    runs = 1
                    extras['w'] += 1
                    bowling_team[data.group(1)]['R'] += int(runs)
                    bowling_team[data.group(1)]['WD'] += 1
                    current_over_runs += int(runs)
                    continue
                elif 'no ball' in data.group(3).lower():
                    lbdata = re.match(r'(.*?) to (.*?),\s*(.*)?,',lines)
                    addingExtras(data,lines,lbdata.group(3)+' '+lbdata.group(4))
                    if re.match('\d+',lbdata.group(4)):
                        runs = int(scores[lbdata.group(4)])
                    else:
                        runs = int(lbdata.group(4))
                elif 'no run' in data.group(3).lower():
                    runs = 0
                    addingBatsmenData(data,lines,runs)
                elif re.match(r'\s*\d+',data.group(3)):
                    runs = re.match(r'\s*\d+',data.group(3)).group()
                    addingBatsmenData(data,lines,runs)
                else:
                    runs = scores[data.group(3).lower()]
                    addingBatsmenData(data,lines,runs)
                if data.group(1) not in bowling_team:
                    bowling_team[data.group(1)] = {'O':0,'M':0,'R':0,'W':0,'NB':0,'WD':0,'ECO':0.0}
                    bowling_team[data.group(1)]['O'] += 0.1
                    current_over_runs += int(runs)
                    bowling_team[data.group(1)]['R'] += int(runs)
                else:
                    bowling_team[data.group(1)]['O'] += 0.1
                    current_over_runs += int(runs)
                    bowling_team[data.group(1)]['R'] += int(runs)
                    if round(math.modf(bowling_team[data.group(1)]['O'])[0],2) == 0.6:
                        bowling_team[data.group(1)]['O'] =  math.ceil(bowling_team[data.group(1)]['O']) 
                        if current_over_runs == 0:
                            bowling_team[data.group(1)]['M'] += 1
                        current_over_runs = 0

def calculatingEconomy(bowling_team):
    for bowler in bowling_team:
        bowling_team[bowler]['ECO'] = round(bowling_team[bowler]['R']/bowling_team[bowler]['O'],4)

def calculating_SR(batting_team):
    for batsmen in batting_team:
        batting_team[batsmen]['SR'] = round((batting_team[batsmen]['R']/batting_team[batsmen]['B'])*100,3) 

def totalRuns(batting_team,extras):
    total_runs = 0
    for batsmen in batting_team:
        total_runs += batting_team[batsmen]['R']
    for extra in extras:
        total_runs += extras[extra]
    return total_runs

def totalWickets(bowling_team):
    total_wick = 0
    for bowler in bowling_team:
        total_wick += bowling_team[bowler]['W']
    return total_wick

def totalOvers(bowling_team):
    total_overs = 0
    for bowler in bowling_team:
        total_overs += bowling_team[bowler]['O']
    return total_overs

def totalExtras(extras):
    total_extras = 0
    for extra in extras:
        total_extras += extras[extra]
    return total_extras

def creatingScorecard(bat_name,bowl_name,batting_team,bowling_team,extras):
    root = Tk()
    root.title("Cricket Scorecard")
    frame = LabelFrame(root,text='Batting Team',pady=10,padx=10,fg='#de0404',bd=10,font=('Ariel',16,'bold'))
    frame.grid(row=0,column=0)
    batsmens = list(batting_team.keys())
    stats = list(batting_team.values())
    curr_row = 0

    Label(frame,text=bat_name,font=('Arial',14,'bold')).grid(row=0,column=0)
    batting_details = ['Batsmen','','R','B','4s','6s','SR']

    for i in range(len(batting_details)):
        e = Label(frame,text=batting_details[i],width=14,fg='#2570cc',font=('Arial',12,'bold'))
        e.grid(row=1,column=i)


    for i in range(len(batsmens)):
        e = Label(frame,text=batsmens[i],width=15,font=('Arial',12))
        e.grid(row=i+2,column=0)
        stat = list(stats[i].values())
        for j in range(1,len(stat)+1):
            if j == 1:
                e = Label(frame,text=stat[j-1],width=25,font=('Arial',12))
                e.grid(row=i+2,column=j)
            else:
                e = Label(frame,text=stat[j-1],width=8,font=('Arial',12))
                e.grid(row=i+2,column=j)

        curr_row = i+2

    extras_frame = LabelFrame(root,text='Extras',fg='#de0404',bd=10,font=('Arial',16,'bold'))
    extras_frame.grid(row=1,column=0)
    Label(extras_frame,text='Extras',font=('Arial',14,'bold')).grid(row=0,column=0)
    extras_string = "("+'b: '+str(extras['b'])+', lb: '+str(extras['lb'])+', w: '+str(extras['nb'])+")"
    Label(extras_frame,text= str(totalExtras(extras))+" "+extras_string,font=('Arial',12)).grid(row=0,column=1)

    total_frame = LabelFrame(root,text='Total',fg='#de0404',bd=8,font=('Arial',16,'bold'))
    total_frame.grid(row=2,column=0)
    Label(total_frame,text='Total',width=7,font=('Arial',14,'bold')).grid(row=0,column=0)
    Label(total_frame,text= str(totalRuns(batting_team,extras))+"-"+str(totalWickets(bowling_team))+" ("+str(totalOvers(bowling_team))+' Ovr)',fg='#e60000',font=('Arial',13,'bold')).grid(row=0,column=1)


    bottomFrame = LabelFrame(root,text="Bowling Team",pady=10,padx=10,fg='#de0404',bd=10,font=('Ariel',16,'bold'))
    bottomFrame.grid(row=3,column=0)
    Label(bottomFrame,text=bowl_name,font=('Arial',14,'bold')).grid(row=0,column=0)
    curr_row = curr_row +2


    bowlers = list(bowling_team.keys())
    stats = list(bowling_team.values())
    bowling_details = ['Bowler','O','M','R','W','NB','WD','ECO']

    for i in range(len(bowling_details)):
        e = Label(bottomFrame,text=bowling_details[i],width=13,fg='#2570cc',font=('Arial',12,'bold'))
        e.grid(row=1 ,column=i)
    curr_row += 1

    for i in range(len(bowlers)):
        e = Label(bottomFrame,text=bowlers[i],width=15,font=('Arial',12))
        e.grid(row=i+2,column=0)
        stat = list(stats[i].values())
        for j in range(1,len(stat)+1):
            e = Label(bottomFrame,text=stat[j-1],width=5,font=('Arial',12))
            e.grid(row=i+2,column=j)
     
    root.mainloop()

if __name__ == "__main__":
    start()
    calculating_SR(batting_team)
    calculatingEconomy(bowling_team)
    print("Total runs scored: "+str(totalRuns(batting_team,extras)))
    print("Total wickets taken: "+str(totalWickets(bowling_team)))
    print("Total Extras conceded: "+str(totalExtras(extras)))
    print(extras)
    print("Batting team data:")
    print(batting_team)
    print('\n')
    print("Bowling team data:")
    print(bowling_team)
    print('\n')
    bat_name = 'KKR'
    bowl_name = 'KXIP'
    creatingScorecard(bat_name,bowl_name,batting_team,bowling_team,extras)