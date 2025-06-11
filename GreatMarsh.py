import math

import csv

def load_pokemon_data(filename):
    pokemon_data = {}
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['NAME'].upper().strip()
            catch_rate = int(row['Catch Rate'])
            flee_rate = int(row['Flee Rate'])
            pokemon_data[name] = (flee_rate, catch_rate)
    return pokemon_data

_pokemon_data = None

def get_fc(name):
    '''
    name (STR) -> Name of a Pokemon that can be found in PKMN_list.txt
    Returns (flee(INT), catch(INT))
    '''
    global _pokemon_data
    if _pokemon_data is None:
        _pokemon_data = load_pokemon_data('PKMN_list.txt')
    
    name = name.upper().strip()
    return _pokemon_data[name]

def calculate_catch_odds(rate, catch=6):
    '''Intakes the current stage of catch
    '''
    # pull the modified catch rate
    rate = get_modified_rate(rate, catch)
    # calculate catch rate after ball and health (full health with a safari ball)
    a = (rate * 1.5 / 3)
    if a >= 255:
        p = 1    
    else:
        # odds of a shake
        b = ('0xffff0', 16)/((math.sqrt((
                 math.sqrt(('0xff0000', 16)/a))))))        
        # odds of successful capture
        p = pow((b/65536), 4)
    return p

def get_modified_rate_old(rate, mod=6):
    '''
    Returns the modifed rate based off of the current
    stat buff/debuff
    6 being netural
    '''
    if mod == 6:
        return rate
    elif mod < 6:
        return int(2/(8-mod)*rate)
    else:
        return int((mod-4)/2*rate)

def get_modified_rate(rate, mod=6):
    '''
    Returns the modifed rate based off of the current
    stat buff/debuff
    6 being netural
    '''
    if mod == 6:
        return rate
    elif mod == 5:
        return (rate*10/15)
    elif mod == 4:
        return (rate*10/20)
    elif mod == 3:
        return (rate*10/25)
    elif mod == 2:
        return (rate*10/30)
    elif mod == 1:
        return (rate*10/35)
    elif mod == 0:
        return (rate*10/40)
    elif mod == 7:
        return (rate*15/10)
    elif mod == 8:
        return (rate*20/10)
    elif mod == 9:
        return (rate*25/10)
    elif mod == 10:
        return (rate*30/10)
    elif mod == 11:
        return (rate*35/10)
    elif mod == 12:
        return (rate*40/10)

def calculate_flee_odds(rate, mod=6):
    '''
    
    '''
    rate = get_modified_rate(rate, mod)
    odds = (rate + 1)/255
    return min(1, odds)

def m(rate, thrown=6, z=1):
    while mod <= 6:
        z *= 1 - (((rate*2/(thrown + 2)) + 1)/255)
        mod += 1
    return z

def b(y, z=6, p=1, rate=60):
    if 0 > y or y >= z:
        return p
    else:
        return t(y, z, p)
     
def t(y, z, p, rate=60):
    print("odds: " + str(p * (1 - (((rate*2/(y+2))+1)/255))))
    return b(y + 1, z, p * (1 - (((rate*2/(y+2))+1)/255)))
    
def odds_of_catch(p_turn, p_catch, p_flee):
    '''FOR ODDS BY TURN - TAKES INTO ACCOUNT ODDS OF GETTING TO SAID TURN'''
    # The probability to catch on any ball throw is:
    # the odds of getting to the turn x the odds of catching with one ball
    p_catch_new = p_catch * p_turn
    # The odds of flee after any ball throw is:
    # the odds of getting to the turn x the odds of not catching * odds of flee
    p_flee = (1 - p_catch) * p_turn * p_flee
    # the odds to get to the next turn is just whatever is left over
    p_continue = p_turn - p_catch_new - p_flee
    return (p_continue, p_catch_new, p_flee)


def balls_only_catch(pokemon):
    '''
    USED TO GET THE ODDS OF CAPTURE WITHOUT ANY BAIT
    INT catch_rate - the pokemons base catch rate
    INT flee_rate - base flee rate
    '''
    if isinstance(pokemon, str):
        fc = get_fc(pokemon)
        catch_rate = fc[1]
        flee_rate = fc[0]
    else:
        catch_rate = pokemon[1]
        flee_rate = pokemon [0]
    # get the odds of capture per ball
    p_catch = calculate_catch_odds(catch_rate, 6)
    # get odds of fleeing per ball
    p_flee = calculate_flee_odds(flee_rate, 6)
    # Run the first turn
    round_vals = odds_of_catch(1, p_catch, p_flee)
    p_success = round_vals[1]
    p_failure = round_vals[2]
    balls = 1
    #Throw balls until we run out
    while balls < 30:
        round_vals = odds_of_catch(round_vals[0], p_catch, p_flee)
        p_success += round_vals[1]
        p_failure += round_vals[2]
        balls += 1
    p_failure += round_vals[0]
    #Return the probability of successfully catching vs not
    return (p_success, p_failure)

def one_bait_catch(pokemon):
    '''
    USED TO GET THE ODDS OF CAPTURE WITH ONE BAIT
    INT catch_rate - the pokemons base catch rate
    INT flee_rate - base flee rate
    '''
    if isinstance(pokemon, str):
        fc = get_fc(pokemon)
        catch_rate = fc[1]
        flee_rate = fc[0]
    else:
        catch_rate = pokemon[1]
        flee_rate = pokemon [0]
    # get the odds of capture per ball
    p_catch = calculate_catch_odds(catch_rate, 6)
    # get odds of fleeing per ball
    p_flee = calculate_flee_odds(flee_rate, 6)
    # Run the first turn
    p_failure = p_flee
    p_success = 0
    p_turn = 1 - p_flee
    p_catch = calculate_catch_odds(catch_rate, 7)
    for i in (6, 7):
        balls = 0
        round_vals = [1]
        if i == 6:
            round_vals[0] = p_turn * 0.1
        else:
            round_vals[0] = p_turn * 0.9
        p_flee = calculate_flee_odds(flee_rate, i)
        #Throw balls until we run out
        while balls < 30:
            round_vals = odds_of_catch(round_vals[0], p_catch, p_flee)
            p_success += round_vals[1]
            p_failure += round_vals[2]
            balls += 1
        p_failure += round_vals[0]
        #Return the probability of successfully catching vs not
    return (p_success, p_failure)

def one_mud_catch(pokemon):
    '''
    USED TO GET THE ODDS OF CAPTURE WITH ONE BAIT
    INT catch_rate - the pokemons base catch rate
    INT flee_rate - base flee rate
    '''
    if isinstance(pokemon, str):
        fc = get_fc(pokemon)
        catch_rate = fc[1]
        flee_rate = fc[0]
    else:
        catch_rate = pokemon[1]
        flee_rate = pokemon [0]
    # get the odds of capture per ball
    p_catch = calculate_catch_odds(catch_rate, 6)
    # get odds of fleeing per ball
    p_flee = calculate_flee_odds(flee_rate, 6)
    # Run the first turn
    p_failure = p_flee
    p_success = 0
    p_turn = 1 - p_flee
    p_flee = calculate_flee_odds(flee_rate, 5)
    for i in (5, 6):
        balls = 0
        round_vals = [1]
        if i == 6:
            round_vals[0] = p_turn * 0.1
        else:
            round_vals[0] = p_turn * 0.9
        p_catch = calculate_catch_odds(catch_rate, i)
        #Throw balls until we run out
        while balls < 30:
            round_vals = odds_of_catch(round_vals[0], p_catch, p_flee)
            p_success += round_vals[1]
            p_failure += round_vals[2]
            balls += 1
        p_failure += round_vals[0]
        #Return the probability of successfully catching vs not
    return (p_success, p_failure)

def pretty_output(pokemon, n=3):
    print('POKEMON: ' + str(pokemon))
    fc = get_fc(pokemon)
    flee_rate = fc[0]
    print('Flee rate: ' + str(flee_rate))
    p_flee = calculate_flee_odds(flee_rate)
    print('Odds to flee per turn: ' + 
          str(round((p_flee * 100), 2)) + "%")
    catch_rate = fc[1]
    print('Catch rate: ' + str(catch_rate))
    p_catch = calculate_catch_odds(catch_rate)
    print('Odds of capture per ball: ' +
          str(round((p_catch * 100), 2)) + "%")
    boo = balls_only_catch(pokemon)
    print('Odds of success with balls only: ' +
          str(round((boo[0] * 100), 2)) + "%")
    if n>=2:
        obo = one_bait_catch(pokemon)
        print('Odds of success starting with one bait: ' +
              str(round((obo[0] * 100), 2)) + "%")
    if n>=3:
        omo = one_mud_catch(pokemon)
        print('Odds of success starting with one mud: ' +
              str(round((omo[0] * 100), 2)) + "%")

def all_pretty(n=3):
    names = ['ARBOK', 'GOLDUCK', 'GYARADOS', 'NOCTOWL', 'MARILL', 'QUAGSIRE', 'ROSELIA', 'TROPIUS', 'STARAVIA', 'BIBAREL', 'DRAPION',
             'CARNIVINE', 'PSYDUCK', 'TANGELA', 'MAGIKARP', 'HOOTHOOT', 'CARVANHA', 'STARLY', 'BIDOOF', 'PARAS', 'EXEGGCUTE',
             'YANMA', 'WOOPER', 'SHROOMISH', 'AZURILL', 'GULPIN', 'BARBOACH', 'KEKLEON', 'BUDEW', 'SKORUPI', 'TOXICROAK',
             'KANGASKHAN', 'CROAGUNK', 'WHISCASH']
    for name in names:
        pretty_output(name,n)
        print()

def get_pokemon_data():
    f = open("PKMN_list.txt", "r")
    lines = f.readlines()
    # Strips the newline character    
    lines_stripped = []
    for line in lines[1:]:
        curr = list(line.strip().split(', '))
        curr[0] = int(curr[0])
        curr[2] = int(curr[2])
        curr[3] = int(curr[3])
        lines_stripped.append(curr)
    lines_stripped.sort()
    return lines_stripped

def all_pretty_jhoto(n=3):
    pokemons = get_pokemon_data()
    for pokemon in pokemons:
        pretty_output_jhoto(pokemon[1], pokemon[2], pokemon[3] ,n)
        print()    

def pretty_output_jhoto(pokemon, catch_rate, flee_rate, n=3):
    print('POKEMON: ' + str(pokemon))
    print('Flee rate: ' + str(flee_rate))
    p_flee = calculate_flee_odds(flee_rate)
    print('Odds to flee per turn: ' + 
          str(round((p_flee * 100), 2)) + "%")
    print('Catch rate: ' + str(catch_rate))
    p_catch = calculate_catch_odds(catch_rate)
    print('Odds of capture per ball: ' +
          str(round((p_catch * 100), 2)) + "%")
    boo = balls_only_catch((flee_rate, catch_rate))
    print('Odds of success with balls only: ' +
          str(round((boo[0] * 100), 2)) + "%")
    if n>=2:
        obo = one_bait_catch((flee_rate, catch_rate))
        print('Odds of success starting with one mud: ' +
              str(round((obo[0] * 100), 2)) + "%")
    if n>=3:
        omo = one_mud_catch((flee_rate, catch_rate))
        print('Odds of success starting with one bait: ' +
              str(round((omo[0] * 100), 2)) + "%")


def combo_tests():
    names = ['ARBOK', 'GOLDUCK', 'GYARADOS', 'NOCTOWL', 'MARILL', 'QUAGSIRE', 'ROSELIA', 'TROPIUS', 'STARAVIA', 'BIBAREL', 'DRAPION',
             'CARNIVINE', 'PSYDUCK', 'TANGELA', 'MAGIKARP', 'HOOTHOOT', 'CARVANHA', 'STARLY', 'BIDOOF', 'PARAS', 'EXEGGCUTE',
             'YANMA', 'WOOPER', 'SHROOMISH', 'AZURILL', 'GULPIN', 'BARBOACH', 'KEKLEON', 'BUDEW', 'SKORUPI', 'TOXICROAK',
             'KANGASKHAN', 'CROAGUNK']    
    for name in names:
        fc = get_fc(name)
        print(name)
        flee = get_modified_rate(fc[0], 7)
        catch = get_modified_rate(fc[1], 7)
        name = (flee, catch)
        pretty_output(name)
        print()

if __name__ == '__main__':
    print("GENERATION 4 GREAT MARSH ZONE CALCULATOR")
    #all_pretty(1)
    all_pretty_jhoto(3)
    input("DONE")
