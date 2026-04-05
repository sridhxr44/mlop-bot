#modules
import random
import requests

#i will add the details like rules and stats later. rn this is just a rough sketch
#c for cop, p for politician, r for robber
p1 = int(input("player1 choose: 1 for cop, 2 for robber, 3 for politician: "))-1
p2 = random.choice([x for x in [0, 1, 2] if x != p1])
print(f"Bot chose: {['Cop', 'Robber', 'Politician'][p2]}")
print("--------------------------------------------------------------")

#stats,0 for cop, 1 for robber, 2 for politician 
hpdmg = [[25,2],[13,3],[12,4]]#[hp,dmg] of each character, fixed
#set stats for players
p1h = hpdmg[p1][0]#hp
p2h = hpdmg[p2][0]#hp
p1d = hpdmg[p1][1]#base dmg
p2d = hpdmg[p2][1]#base dmg
plyr = [                    #[character type, hp, basedmg,maxhp(fixed),ability3 uses,stats]
    [p1,p1h,p1d,p1h,1,[False,False,False,False,False]],     #stats include [dmgred_active,immun_active,dmg_bonus_active,skip_active,cooldown]
    [p2,p2h,p2d,p2h,1,[False,False,False,False,False]]
    ]


#who goes first? one with lower hp
atkr = -1
if plyr[0][1] == plyr[1][1]:
    atkr = random.choice([0,1])
elif plyr[0][1] < plyr[1][1]:
    atkr = 0#player1 is attacking
else:
    atkr = 1#player2 is attacking
#functions
    

        
#weakness: 0>1 , 1>2, 2>0 (as per index, not mathematically) only cop v robber, others are removed
def fin_dmg(atk,dfd,basedmg):
    dmg = random.randint(basedmg-1,basedmg+1)
    if atk == 0 and dfd == 1:
        print("+1 damage from advantage")
        dmg+=1     #c +1 dmg against r
    #if atk == 2 and dfd == 1:
        #print("-1 damage from advantage")
        #dmg-=1     #p -1 dmg against r
    #if atk == 2 and dfd == 0:
        #print("+1 damage from advantage")
        #dmg+=1     #p +1 dmg against c
    return dmg
def ab2(plyr,atkr):
    if plyr[atkr][0]==0:    #cop
        return [0,0,[0,0,1,0,0]]
    elif plyr[atkr][0]==1:  #robber
        return [1,1,[0,0,0,0,0]]
    elif plyr[atkr][0]==2:  #politician
        return [0,0,[1,0,0,0,0]]
def ab3(plyr,atkr):
    if plyr[atkr][0]==0:    #cop
        return [1,5,[0,0,0,0,0]]
    elif plyr[atkr][0]==1:  #robber
        return [0,0,[0,0,0,1,0]]
    elif plyr[atkr][0]==2:  #politician
        return [0,0,[0,1,0,0,0]]
def action(plyr,atkr,choice):
    #return lists: [dmg,heal,[dmg_red_active,immune_active,dmg_bonus_active,skip_active,cd_active]]
    if choice == 1:
        #flat damage.
        return [fin_dmg(plyr[atkr][0],plyr[1-atkr][0],plyr[atkr][2]),0,[0,0,0,0,1]]
    elif choice == 2:
        #ability2
        return ab2(plyr,atkr)
    elif choice == 3:
        #ability3
        return ab3(plyr,atkr)
def legit(choice,plyr,atkr):
    if choice not in [1,2,3]:
        return False
    if (choice == 1 and plyr[atkr][5][4] == True) or (choice == 3 and plyr[atkr][4] == 0):
        if choice == 1: print("Ability on cooldown, choose another ability")
        if choice == 3: print("No uses left, choose another ability")
        return False
    return True
def ml_choice(plyr, atkr, last_action):
    state = {
        "my_char": plyr[atkr][0],
        "enemy_char": plyr[1-atkr][0],
        "my_hp": plyr[atkr][1],
        "enemy_hp": plyr[1-atkr][1],
        "my_cd": int(plyr[atkr][5][4]),
        "enemy_cd": int(plyr[1-atkr][5][4]),
        "my_ability3": plyr[atkr][4],
        "enemy_ability3": plyr[1-atkr][4]
    }
    response = requests.post("http://localhost:8000/predict", json=state)
    return response.json()["action"]
#abilitylist, you can read their abilities from here
ab = [
    ["1. Deal 2 damage","2. Gain +1 damage next turn and skip this one","3. Heal +2 health and +1 damage next turn"],#cop
    ["1. Deal 3 damage","2. Deal 1 damage and heal 1 hp","3. Skip opponent's turn"],#robber
    ["1. Deal 4 damage","2. Receive half damage from opponent for 1 turn","3. Become immune to all damages"]#politician
    ]

#testing
turn = 1

#game
last_action = [0, 0]
while plyr[0][1]>0 and plyr[1][1]>0:
    print("ROUND",turn,"\n--------------------------------------------------------------")
    print("Player1 HP:",plyr[0][1],"/",plyr[0][3],"\nPlayer2 HP:",plyr[1][1],"/",plyr[1][3],"\n--------------------------------------------------------------")
    print("Player",atkr+1,"to move")
    print("Choices: ",end="")
    for i in ab[plyr[atkr][0]]:
        print("\n",i,end="")
        if i== ab[plyr[atkr][0]][0]:
            if plyr[atkr][5][4]==True:
                print(" (On cooldown)",end="")
    print("("+str(plyr[atkr][4])+" uses)")
    if atkr == 0:  # human
        choice = 0
        while legit(choice, plyr, atkr) != True:
            choice = int(input("Your choice: "))
    else:  # ML bot
        choice = ml_choice(plyr, atkr, last_action[1-atkr])
        print("Bot chose:", choice)

    last_action[atkr] = choice
    if choice == 3: plyr[atkr][4] = 0
    stats = action(plyr,atkr,choice)
    for i in range(len(stats[2])):
        if stats[2][i]==1:
            plyr[atkr][5][i]=True
    opdmg = stats[0]
    if stats[1]>0:
        print("Healed +"+str(min(plyr[atkr][3]-plyr[atkr][1],stats[1]))+" HP")
        plyr[atkr][1]+=min(plyr[atkr][3]-plyr[atkr][1],stats[1])
        print("Player",atkr+1,"HP:",plyr[atkr][1],"/",plyr[atkr][3])
##    for i in range(len(stats[2])):
##        if stats[2][i]==1:
##            plyr[atkr][5][i]=True
    #outputs
    if plyr[atkr][5][2]==True:
        if choice ==1:  #adding bonus damage first
            opdmg+=1
            print("+1 bonus damage")
            plyr[atkr][5][2]=False
        elif choice == 3:
            plyr[atkr][5][2] = False
    if plyr[1-atkr][5][0]==True:    #if defender has dmg red
        print(opdmg,"damage reduced by 50% (floor), Final Damage:",int(opdmg/2))
        opdmg=int(opdmg/2)
        plyr[1-atkr][5][0] = False
    if plyr[1-atkr][5][1]==True:    #if defender has immunity
        print("Player",(1-atkr)+1,"is immune to damage this round")
        opdmg=0
        plyr[1-atkr][5][1] = False
    if opdmg>0:
        print("Player",(1-atkr)+1,"received",opdmg,"damage.")
        plyr[1-atkr][1]-=min(opdmg,plyr[1-atkr][1])
    if choice !=1:  plyr[atkr][5][4]=False
    if plyr[atkr][5][3]==True:
        turn+=1
        print("--------------------------------------------------------------\nROUND",turn,"\n--------------------------------------------------------------")
        print("Player1 HP:",plyr[0][1],"/",plyr[0][3],"\nPlayer2 HP:",plyr[1][1],"/",plyr[1][3],"\n--------------------------------------------------------------")
        print("Player",(1-atkr)+1,"has their moves for this round disabled.")
        plyr[atkr][5][3]=False
        plyr[1-atkr][5][4]=False
        atkr=1-atkr
    print("--------------------------------------------------------------")    
    atkr = 1-atkr
    turn+=1
print("Player1 HP:",plyr[0][1],"/",plyr[0][3],"\nPlayer2 HP:",plyr[1][1],"/",plyr[1][3],"\n--------------------------------------------------------------")
if plyr[0][1]>plyr[1][1]:
    print("player 1 won")
else:
    print("player 2 won")
winner = 1 - (1 if plyr[0][1] > plyr[1][1] else 0)
requests.post("http://localhost:8000/end_game", json={"win": winner})
