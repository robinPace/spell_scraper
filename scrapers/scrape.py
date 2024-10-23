import requests

from bs4 import BeautifulSoup
import pandas as pd
import time, re

def detect_verbal(components):
    return components.startswith('V')

def detect_somatic(components):
    splitParts = components.split(',')

    if(detect_verbal(components)):
        return len(splitParts) > 1 and splitParts[1].strip() == 'S'
    
    return splitParts[0].strip() == 'S'

def detect_materials(components):
    splitParts = [part.strip() for part in components.split(',')]
    length = len(splitParts)

    if(detect_verbal(components) and detect_somatic(components)):
        return length > 2 and splitParts[2].startswith('M')
    elif(detect_verbal(components) or detect_somatic(components)):
        return length > 1 and splitParts[1].startswith('M')
    else:
       return length > 0 and splitParts[0].startswith('M')
    

def check_material_cost(components):
    if '(' not in components:
        return False
    
    allCost = components.split('(')[1]
    cost = re.findall(r'\d (?:\wp|gold)', allCost)

    return bool(cost)

def find_damage(string, higherLevel, spellLevel):
    dmg = []
    damage = re.findall(r' \d+d\d+', string)
    if not damage:
        return "-1"

    print(spellLevel)
    damage = damage[0].strip()
    splitDmg = damage.split('d')
    dmg.append(f"{spellLevel}: {damage}")

    if higherLevel:
        diceTotal = int(splitDmg[0]) + 1
        
        upCasting = re.findall(r" \d\w\w level or higher", higherLevel)
        actualIncrease = re.findall("damage increases", higherLevel)

        if upCasting and actualIncrease:
            for count in range (int(upCasting[0][1]), 10):
                dmg.append(f"{count}: {diceTotal}d{splitDmg[1]}")
                diceTotal += 1
        elif actualIncrease:
            upCasting = re.findall(r" \d+\w\w level", higherLevel)
            
            for character_level in upCasting:
                thisLevel = character_level[1]
                if(character_level[2].isdigit()):
                    thisLevel = character_level[1:3]

                dmg.append(f"{thisLevel}: {diceTotal}d{splitDmg[1]}")
                diceTotal += 1

    return dmg or "-1"

def checkDamageExists(string):
    damage_types = ["acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic", "piercing", "poison", "psychic", "radiant", "slashing", "thunder", "extra"]
    string = string.strip()

    if(string in damage_types):
        return string
    
    if(re.findall(r"\d+d\d+", string) ):
        return "special"

    return "-1"

def checkForDamage(string, die):
    if " damage" in string:
        string = string.split(" ")

        if string[-1] == '':
            string = string[:-1]

        for wordInx in range(len(string)):
            if '.' in string[wordInx]:
                string[wordInx] = string[wordInx].split('.')[0]
            if ',' in string[wordInx]:
                string[wordInx] = string[wordInx].split(',')[0]
            if '\n' in string[wordInx]:
                string[wordInx] = string[wordInx].split('\n')[0]

        idxD = string.index(die)
        idx = string.index("damage")
        while(idxD > idx):
            tempString = string[idx+1:]
            if("damage" in tempString):
                idx = string.index("damage", idx + 1)
                if(string[idx-1] == 'the'):
                    idx = string.index("damage")
                    break
            else:
                break

        result = string[idx - 1]
        return checkDamageExists(result)
    return "-1"



def findType(string, damage):
    if(damage != "-1"):

        if(damage[0]):
            damage = damage[0]

        dice = re.findall(r"\d\dd\d\d", damage)
        if(not dice):
            dice = re.findall(r"\d\dd\d", damage)
            if(not dice):
                dice = re.findall(r"\dd\d\d", damage)
                if(not dice):
                    dice = re.findall(r"\dd\d", damage)
        dice = dice[0]
        return checkForDamage(string, dice)
        
    return "-1"



# URL of the website to scrape
file = open("links.csv", "r")
file.readline()
urls = file.read().splitlines()
#urls = ["http://dnd5e.wikidot.com/spell:spray-of-cards-ua", "http://dnd5e.wikidot.com/spell:chaos-bolt"]
#urls = ["http://dnd5e.wikidot.com/spell:booming-blade"]

fileName = 'spells.csv'
fileName = 'test.csv'

increment = 0
spell = []
for url in urls:
    # Send an HTTP GET request to the website
    response = requests.get(url)

    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.select(".page-title")
    title = title[0]
    spellName = title.find("span").getText()
    print("Reading ", spellName)

    # Extract the relevant information from the HTML code
    page = soup.find('div', id='page-content')
    count = 0
    castCon = False
    spellSource = "-1"
    spellLevel = "-1"
    spellType = "-1"
    castTime = "-1"
    castRange = "-1"
    castComp = "-1"
    verbal = False
    somatic = False
    material = False
    costlyCompenent = False
    castDur  = "-1"
    spellDesc  = ""
    upCast  = "-1"
    spellLists  = "-1"
    tableData  = False
    listData  = False
    spellAOE = False
    spellAOEsize = "-1"
    spellAOEtype = "-1"
    savingThrow = False
    savingThrowType = "-1"
    dmgDice = "-1"
    dmgType = "-1"
    attackRoll = False
    heal  = False
    pushing = False
    pushDistance = "-1"

    read = page.findAll('p')
    
    for row in read:
        bold = row.find("strong")
        text = row.getText()
        if(bold):
            if(bold.getText() == "Casting Time:"):
                text = text.splitlines()
                for line in text:
                    splitText = line.split(':')
                    if(splitText[0] == "Casting Time"):
                        castTime = splitText[1]
                    elif(splitText[0] == "Range"):
                        aoeSplit = splitText[1].split('(')
                        if(aoeSplit[0] == " Self "):
                            aoeSplit[1] = aoeSplit[1].replace('-', ' ', 2)
                            aoeSplit[1] = aoeSplit[1].replace(' ', '-', 1)
                            aoeSize = aoeSplit[1].split(' ')
                            spellAOE = True
                            spellAOEsize = aoeSize[0]
                            spellAOEtype = aoeSize[1]
                            spellAOEtype = spellAOEtype[:-1]
                            castRange = "Self"
                        elif(aoeSplit[0][-4:] == "Self"):
                            castRange = "Self"
                        elif(aoeSplit[0][-4:] == "cone"):
                            castRange = "Self"
                        else:
                            castRange = splitText[1]
                    elif(splitText[0] == "Components"):
                        castComp = splitText[1]
                    elif(splitText[0] == "Duration"):
                        conSplit = splitText[1].split(',')
                        if(conSplit[0] == " Concentration"):
                            castCon = True
                            castDur = conSplit[1]
                        else:
                            castDur = splitText[1]
            elif(bold.getText() == "Range:"):
                splitText = text.split(':')
                aoeSplit = splitText[1].split('(')
                if(aoeSplit[0] == " Self "):
                    aoeSplit[1] = aoeSplit[1].replace('-', ' ', 2)
                    aoeSplit[1] = aoeSplit[1].replace(' ', '-', 1)
                    aoeSize = aoeSplit[1].split(' ')
                    spellAOE = True
                    spellAOEsize = aoeSize[0]
                    spellAOEtype = aoeSize[1]
                    spellAOEtype = spellAOEtype[:-1]
                    castRange = "Self"
                else:
                    castRange = splitText[1]
            elif(bold.getText() == "Components:"):
                splitText = text.split(':')
                castComp = splitText[1]
            elif(bold.getText() == "Duration:"):
                splitText = text.split(':')
                conSplit = splitText[1].split(',')
                if(conSplit[0] == " Concentration"):
                    castCon = True
                    castDur = conSplit[1]
                else:
                    castDur = splitText[1]
            elif(bold.getText() == "At Higher Levels" or bold.getText() == "At Higher Levels." or bold.getText() == "At Higher Levels:"):
                splitText = text.split('.', 1)
                if(splitText[0] == "At Higher Levels"):
                    upCast = splitText[1]
                else:
                    splitText2 = text.split(':', 1)
                    if(splitText2[0] == "At Higher Levels"):
                        upCast = splitText2[1]
                    else:
                        save = text[:16]
                        if(save == "At Higher Levels"):
                            upCast = text[16:]
                        else:
                            splitText = text.split('\n',1)
                            spellDesc = splitText[0]
                            splitText2 = splitText[1].split('.', 1)
                            upCast = splitText2[1]
                    
            elif(bold.getText() == "Spell Lists" or (bold.getText()).lower() == "spell lists." or bold.getText() == "Spell Lists:"):
                splitText = text.split('.', 1)
                if(splitText[0].lower() == "spell lists"):
                    spellLists = splitText[1]
                else:
                    splitText2 = text.split(':', 1)
                    if(splitText2[0] == "Spell Lists"):
                        spellLists = splitText2[1]
            else:
                spellDesc += '\n'
                spellDesc += text


        else:
            splitText = text.split(':', 1)
            
            if(splitText[0] == "Source"):
                spellSource = splitText[1]
            else:
                if(count == 0):
                    splitText = text.split(' ')
                    if(splitText[1] == "cantrip"):
                        spellLevel = 0
                        spellType = splitText[0]
                    else:
                        spellLevel = splitText[0][0]
                        spellType = splitText[1]
                    count = count + 1
                else:
                    spellDesc += text
                    spellDesc += '\n'
    read = page.findAll('ul')
    for row in read:
        text = row.getText().strip()
        spellDesc = spellDesc + '-' + text + ' '


    if(not spellAOE):
        size = re.findall(r"\d\d\d-foot", spellDesc)
        if(not size):
            size = re.findall(r"\d\d-foot", spellDesc)
            if(not size):
                size = re.findall(r"\d-foot", spellDesc)

        if(size):
            spellAOE = True
            spellAOEsize = size[0]
            size = spellAOEsize
            shape = spellDesc.split(size)[1].strip()
            shape = shape.split(' ')[0]
            shape = shape.split('.')[0]
            if(shape[-1] == '.' or shape[-1] == ','):
                shape = shape[:-1]
            if(shape[0] == '-'):
                shape = shape[1:]
            spellAOEtype = shape

    if(spellAOE):
        if(spellAOEtype[:3] == "by-"):
            spellAOEtype = "special"
        elif(spellAOEtype == "tall" or spellAOEtype=="high"):
            spellAOEtype = "special"
        elif(spellAOEtype == "radiu"):
            spellAOEtype = "radius"
        elif(spellAOEtype == "squares)"):
            spellAOEtype = "square"
        elif(spellAOEtype == "cubes"):
            spellAOEtype = "cube"
    


    if "saving throw" in spellDesc:
        savingThrow = True
        if "Strength" in spellDesc:
            savingThrowType = "strength"
        elif "Dexterity" in spellDesc:
            savingThrowType = "dexterity"
        elif "Constitution" in spellDesc:
            savingThrowType = "constitution"
        elif "Intelligence" in spellDesc:
            savingThrowType = "intelligence"
        elif "Wisdom" in spellDesc:
            savingThrowType = "wisdom"
        elif "Charisma" in spellDesc:
            savingThrowType = "charisma"

        made = "advantage on " + savingThrowType + " saving throws"
        if made in spellDesc:
            savingThrowType = "-1"
            savingThrow = False

        if savingThrowType == '-1':
            savingThrow = False


    if "spell attack" in spellDesc or "melee attack" in spellDesc:
        attackRoll = True
    if "natural weapon" in spellDesc:
        attackRoll = True

    if "melee attack against a" in spellDesc or "makes a melee attack through it" in spellDesc:
        attackRoll = False

    if "hit points" in spellDesc:
        if ("regain" in spellDesc) or ("temporary" in spellDesc):
            heal = True
            if "hit points until" in spellDesc:
                heal = False

    dmgDice = find_damage(spellDesc, upCast, spellLevel)

        
    dmgType = findType(spellDesc, dmgDice)
    if heal:
        dmgType = 'heal'
        if dmgDice == "-1":
            print("Set amount")
    
    if(not dmgDice or heal):
        spellAOE = False
    
    if not dmgType:
        dmgDice = ""

    if "pushed " in spellDesc:
        pushing = True
        pushDistance = re.findall(r" \d\d feet away", spellDesc)
        if not pushDistance:
            pushDistance = re.findall(r" /d feet away", spellDesc)
        if not pushDistance:
            pushDistance = re.findall(r" /d/d feet directly away", spellDesc)
        if not pushDistance:
            pushDistance = re.findall(r" /d feet directly away", spellDesc)
        
        if pushDistance:
            pushDistance = pushDistance[0]
            saved = pushDistance[1]

            if pushDistance[2].isnumeric:
                saved = saved + pushDistance[2]

            pushDistance = saved
        else:
            pushDistance = "To one side"



    
    table = page.findAll('tr')

    if(table):
        tableData = True

    spellSource = spellSource.strip()
    spellType = spellType.strip()
    castTime = castTime.strip()
    castRange = castRange.strip()
    castComp = castComp.strip()
    castDur = castDur.strip()
    spellDesc = spellDesc.strip()
    upCast = upCast.strip()
    spellLists = spellLists.strip()

    verbal = detect_verbal(castComp)
    somatic = detect_somatic(castComp)
    material = detect_materials(castComp)

    if(material):
        costlyCompenent = check_material_cost(castComp)


    spell.append([spellName, spellSource, spellType, spellLevel, castTime, castRange, castComp, verbal, somatic, material, costlyCompenent,
            castDur, castCon, spellDesc, spellAOE, spellAOEsize, spellAOEtype, savingThrow, savingThrowType,
            dmgDice, dmgType, attackRoll, heal, pushing, pushDistance, upCast, spellLists, tableData])
    
    # Add a delay between requests to avoid overwhelming the website with requests
    time.sleep(.05)




# Store the information in a pandas dataframe
df = pd.DataFrame(spell, columns=['Name', 'Source', 'Type', 'Level', 'Cast_Time', 'Range', 'Components', 'Verbal', 'Somatic', 'Material', 'Material_Cost',
        'Duration', 'Concentration', 'Description', 'AOE', 'AOE_size', 'AOE_shape', 'Saving_Throw', 'Saving_Throw_Type',
        'Damage', 'Damage_Type', 'Attack_Roll', 'Healing', 'Pushing', 'Push_Distance','At_Higher_Levels', 'Spell_Lists', 'More'])

file.close()
df.to_csv(fileName, index=False)

