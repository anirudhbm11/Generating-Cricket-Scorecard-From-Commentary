import re
import pdb
import math

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

def addingBowlerData(data,lines,runs):
    pass

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
        batting_team[batsmen]['SR'] = round((batting_team[batsmen]['R']/batting_team[batsmen]['B']),4) * 100

def totalRuns(batting_team,extras):
    total_runs = 0
    for batsmen in batting_team:
        total_runs += batting_team[batsmen]['R']
    for extra in extras:
        total_runs += extras[extra]
    return total_runs

def totalExtras(extras):
    total_extras = 0
    for extra in extras:
        total_extras += extras[extra]
    return total_extras

if __name__ == "__main__":
    start()
    calculating_SR(batting_team)
    calculatingEconomy(bowling_team)
    print(totalRuns(batting_team,extras))
    print(totalExtras(extras))
    print(batting_team)
    print(bowling_team)
    print(extras)
