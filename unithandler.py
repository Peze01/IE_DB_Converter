import ie3locations as iel
import ie3dictionary as iedict

replace_accents = {"A1": "Ù",
                   "A2": "Ú",
                   "A3": "Û",
                   "A4": "Ü",
                   "A6": "Í",
                   "A7": "Ï",
                   "A8": "Ð",
                   "A9": "Ñ",
                   "AA": "Ò",
                   "AB": "Ó",
                   "AC": "Ô",
                   "AE": "Ö",
                   "AF": "Ø",
                   "B1": "à",
                   "B2": "á",
                   "B3": "â",
                   "B4": "ã",
                   "B5": "ä",
                   "B7": "æ",
                   "B8": "ç",
                   "B9": "è",
                   "BA": "é",
                   "BB": "ê",
                   "BC": "ë",
                   "BD": "ì",
                   "BE": "î",
                   "BF": "î",
                   "C0": "ï",
                   "C1": "ð",
                   "C2": "ñ",
                   "C3": "ò",
                   "C5": "ô",
                   "C6": "õ",
                   "C7": "ö",
                   "C9": "ù",
                   "CA": "ú",
                   "CB": "û",
                   "CC": "ü",
                   "CD": "ý",
                   "D0": "À",
                   "D1": "Á",
                   "D2": "Â",
                   "D3": "Ã",
                   "D4": "Ä",
                   "D6": "Æ",
                   "D7": "Ç",
                   "D8": "È",
                   "D9": "É",
                   "DA": "Ê",
                   "DB": "Ë",
                   "DC": "Ì",
                   "DD": "Î",
                   "81": "\'",
                   "8166": "\'",
}


def tohexid(id):
    id = id[2:]
    if len(id) == 4:
        return (id[2:]+id[:2]).lower()
    if len(id) == 2:
        return (id+'00').lower()
    return (id[1:]+'0'+id[0]).lower()

def correct_id(id):
    id = id[2:] + id[:2]
    for z in range(0, len(id)):
        if len(id) != 2:
            if id[0] == '0':
                id = id[1:]
            else:
                break
    return '0x' + id.upper()

def hex2(input):
    new_input = hex(input)[2:]
    # print(new_input)
    if len(new_input)==1:
        return"0"+new_input
    return new_input

def to_text(bytestring):
    if "96a292e8000000000000000000000000" in bytestring:
        return "No Name"
    
    bytes_as_list = [bytestring[i:i+2] for i in range(0, len(bytestring), 2)]

    # return bytes.fromhex(bytestring).decode(encoding="cp1252", errors="replace").rstrip('\x00')
    finalstring = ""
    four_bit = False
    bytes_as_list = [bytestring[i:i+2] for i in range(0, len(bytestring), 2)]
    for i,current_bytes in enumerate(bytes_as_list):
        to_decode = current_bytes.upper()
        if four_bit:
            finalstring+="\'"
            four_bit = False
            continue
        if to_decode in replace_accents:
            if to_decode == "81" and bytes_as_list[i+1]=="66":
                four_bit = True
                continue
            finalstring+=replace_accents[to_decode]
        else:
            finalstring+=bytes.fromhex(to_decode).decode(encoding="cp1252", errors="replace")
    return finalstring.rstrip('\x00')

    # return bytes.fromhex(str).decode(encoding="utf-8", errors="replace").rstrip('\x00')

def get_all_sections(file,sectionsize):
    sections = []
    for i in range(sectionsize, len(file), sectionsize):
        sections.append(file[i:i+sectionsize])
    return sections

def get_hex(arr, i, locations):
    return arr[i][locations[0]:locations[1]]

def convert_points(value):
    return str(int((value[2:]+value[:2]), 16))

def value_in_dict(value, dict):
    return "Unknown" if value not in dict else dict[value]

def get_binder_id(player_id, unitbasearr,usearcharr):
    binder_id = 0
    for binder_id in range(0, len(usearcharr)):
        if get_hex(usearcharr, binder_id, iel.BINDER_ID) == get_hex(unitbasearr, player_id, iel.PLAYER_ID):
            return binder_id
    return binder_id

def open_unit_files(unitbasepath, unitstatpath, usearchpath):
    with open(unitbasepath, 'rb') as f:
        unitbase = f.read().hex()

    with open(usearchpath, 'rb') as f:
        usearch = f.read().hex()

    with open(unitstatpath, 'rb') as f:
        unitstat = f.read().hex()

    unitbasearr = get_all_sections(unitbase, iel.UNITBASE_LENGTH)
    unitstatarr = get_all_sections(unitstat, iel.UNITSTAT_LENGTH)
    usearcharr = get_all_sections(usearch, iel.USEARCH_LENGTH)

    return unitbase, unitstat, usearch, unitbasearr, unitstatarr, usearcharr


def get_unit_data(unitbasepath, unitstatpath, usearchpath):
    unitbase, unitstat, usearch, unitbasearr, unitstatarr, usearcharr = open_unit_files(unitbasepath, unitstatpath, usearchpath)
    data = []

    for player_id in range(0, len(unitbasearr)):
        binder_id = get_binder_id(player_id, unitbasearr, usearcharr)
        player = {}

        player["Player Hex ID"] = correct_id(get_hex(unitbasearr, player_id, iel.PLAYER_ID))
        player["Full Name"] = to_text(get_hex(unitbasearr, player_id, iel.FULL_NAME))
        player["Nickname"] = to_text(get_hex(unitbasearr, player_id, iel.NICKNAME))
        player["Binder Nickname"] = to_text(get_hex(usearcharr, binder_id, iel.BINDER_NICKNAME))
        player["Position"] = value_in_dict(get_hex(unitbasearr, player_id, iel.POSITION),iedict.POSITION)
        player["Element"] = value_in_dict(get_hex(unitbasearr, player_id, iel.ELEMENT),iedict.ELEMENT)
        player["Gender"] = value_in_dict(get_hex(unitbasearr, player_id, iel.GENDER),iedict.GENDER)
        player["Body Type"] = iedict.get_body_type(get_hex(unitbasearr, player_id, iel.BODY_TYPE), get_hex(unitbasearr, player_id, iel.SPECIAL_BODY_TYPE))
        player["Skin Tone"] = int(get_hex(unitbasearr, player_id, iel.SKIN_TONE),16)

        player["Min FP"] = convert_points(get_hex(unitstatarr, player_id, iel.MIN_FP))
        player["Min TP"] = convert_points(get_hex(unitstatarr, player_id, iel.MIN_TP))
        player["Min Kick"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_KICK), 16))
        player["Min Body"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_BODY), 16))
        player["Min Control"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_CONTROL), 16))
        player["Min Guard"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_GUARD), 16))
        player["Min Speed"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_SPEED), 16))
        player["Min Stamina"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_STAMINA), 16))
        player["Min Guts"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_GUTS), 16))

        player["Min FP"] = convert_points(get_hex(unitstatarr, player_id, iel.MIN_FP))
        player["Min TP"] = convert_points(get_hex(unitstatarr, player_id, iel.MIN_TP))
        player["Min Kick"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_KICK), 16))
        player["Min Body"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_BODY), 16))
        player["Min Control"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_CONTROL), 16))
        player["Min Guard"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_GUARD), 16))
        player["Min Speed"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_SPEED), 16))
        player["Min Stamina"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_STAMINA), 16))
        player["Min Guts"] = str(int(get_hex(unitstatarr, player_id, iel.MIN_GUTS), 16))

        player["FP"] = convert_points(get_hex(unitstatarr, player_id, iel.FP))
        player["TP"] = convert_points(get_hex(unitstatarr, player_id, iel.TP))
        player["Kick"] = str(int(get_hex(unitstatarr, player_id, iel.KICK), 16))
        player["Body"] = str(int(get_hex(unitstatarr, player_id, iel.BODY), 16))
        player["Control"] = str(int(get_hex(unitstatarr, player_id, iel.CONTROL), 16))
        player["Guard"] = str(int(get_hex(unitstatarr, player_id, iel.GUARD), 16))
        player["Speed"] = str(int(get_hex(unitstatarr, player_id, iel.SPEED), 16))
        player["Stamina"] = str(int(get_hex(unitstatarr, player_id, iel.STAMINA), 16))
        player["Guts"] = str(int(get_hex(unitstatarr, player_id, iel.GUTS), 16))

        player["FP Growth"] = str(int(get_hex(unitstatarr, player_id, iel.FP_GROWTH), 16))
        player["TP Growth"] = str(int(get_hex(unitstatarr, player_id, iel.TP_GROWTH), 16))
        player["Kick Growth"] = str(int(get_hex(unitstatarr, player_id, iel.KICK_GROWTH), 16))
        player["Body Growth"] = str(int(get_hex(unitstatarr, player_id, iel.BODY_GROWTH), 16))
        player["Control Growth"] = str(int(get_hex(unitstatarr, player_id, iel.CONTROL_GROWTH), 16))
        player["Guard Growth"] = str(int(get_hex(unitstatarr, player_id, iel.GUARD_GROWTH), 16))
        player["Speed Growth"] = str(int(get_hex(unitstatarr, player_id, iel.SPEED_GROWTH), 16))
        player["Stamina Growth"] = str(int(get_hex(unitstatarr, player_id, iel.STAMINA_GROWTH), 16))
        player["Guts Growth"] = str(int(get_hex(unitstatarr, player_id, iel.GUTS_GROWTH), 16))

        player["Max Stats"] = str(int(correct_id(get_hex(unitstatarr, player_id, iel.MAX_STATS)), 16))

        player["Move 1"] = iedict.MOVES[correct_id(get_hex(unitstatarr, player_id, iel.MOVE_1))]
        player["Move 1 Unlock"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_1_UNLOCK), 16))
        player["Move 1 Level"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_1_LEVEL), 16))

        player["Move 2"] = iedict.MOVES[correct_id(get_hex(unitstatarr, player_id, iel.MOVE_2))]
        player["Move 2 Unlock"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_2_UNLOCK), 16))
        player["Move 2 Level"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_2_LEVEL), 16))

        player["Move 3"] = iedict.MOVES[correct_id(get_hex(unitstatarr, player_id, iel.MOVE_3))]
        player["Move 3 Unlock"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_3_UNLOCK), 16))
        player["Move 3 Level"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_3_LEVEL), 16))

        player["Move 4"] = iedict.MOVES[correct_id(get_hex(unitstatarr, player_id, iel.MOVE_4))]
        player["Move 4 Unlock"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_4_UNLOCK), 16))
        player["Move 4 Level"] = str(int(get_hex(unitstatarr, player_id, iel.MOVE_4_LEVEL), 16))

        player["Recruitment Type"] = iedict.RECRUITMENT_TYPE[get_hex(usearcharr, binder_id, iel.RECRUITMENT_TYPE)]
        player["Location/Team"] = iedict.get_binder_location(get_hex(usearcharr, binder_id, iel.LOCATION),get_hex(usearcharr, binder_id, iel.TEAM))
        player["Overworld Sprite Texture"] = correct_id(get_hex(unitbasearr, player_id, iel.OVERWORLD_SPRITE_TEXTURE))
        player["Overworld Sprite Palette"] = correct_id(get_hex(unitbasearr, player_id, iel.OVERWORLD_SPRITE_PALETTE))

        player["Player ID"] = str(player_id)
        player["Binder ID"] = str(binder_id)

        data.append(player)
    return data


def from_text(text):
    if text == "No Name":
        return "96a292e8000000000000000000000000"
    finalstring = ""
    for char in text:
        for key, val in replace_accents.items():
            if val == text:
                finalstring+=key
                break
        finalstring+=hex(ord(char))[2:]
    return finalstring

def fill_characters(string, length):
    while len(string)<length:
        string+='0'
    return string

def replace_hex(original, location, value):
    return original[:location[0]] + value + original[location[1]:]

def get_key(dict, value):
    for key, val in dict.items():
        if val == value:
            return key
    return None

def to_hex_4bit(value):
    if len(value) == 4: return (value[2:]+value[:2]).lower()
    if len(value) == 3: return (value[1:]+'0'+value[0]).lower()
    if len(value) == 2: return (value+'00').lower()
    return '0' + value.lower() + '00'

def num_to_hex_4bit(value):
    new_value = hex(value)[2:]
    return to_hex_4bit(new_value)

def num_to_hex(value):
    value = hex(value)[2:]
    if len(value) == 2: return value.lower()
    return '0'+ value.lower()

def to_unit_data(data, unitbasepath, unitstatpath, usearchpath):
    unitbase, unitstat, usearch, unitbasearr, unitstatarr, usearcharr = open_unit_files(unitbasepath, unitstatpath, usearchpath)

    def update_unitbase(player):
        new_unitbase = current_unitbase = unitbasearr[int(player["Player ID"])]

        new_unitbase = replace_hex(new_unitbase, iel.FULL_NAME, fill_characters(from_text(player["Full Name"]), 56))
        new_unitbase = replace_hex(new_unitbase, iel.NICKNAME, fill_characters(from_text(player["Nickname"]), 32))
        new_unitbase = replace_hex(new_unitbase, iel.POSITION, get_key(iedict.POSITION, player["Position"]))
        new_unitbase = replace_hex(new_unitbase, iel.ELEMENT, get_key(iedict.ELEMENT, player["Element"]))
        new_unitbase = replace_hex(new_unitbase, iel.GENDER, get_key(iedict.GENDER, player["Gender"]))
        new_unitbase = replace_hex(new_unitbase, iel.BODY_TYPE, iedict.get_key_body_type(player["Body Type"])[0])
        new_unitbase = replace_hex(new_unitbase, iel.SPECIAL_BODY_TYPE, iedict.get_key_body_type(player["Body Type"])[1])
        new_unitbase = replace_hex(new_unitbase, iel.SKIN_TONE, num_to_hex(player["Skin Tone"]))
        new_unitbase = replace_hex(new_unitbase, iel.OVERWORLD_SPRITE_TEXTURE, to_hex_4bit(player["Overworld Sprite Texture"][2:]))
        new_unitbase = replace_hex(new_unitbase, iel.OVERWORLD_SPRITE_PALETTE, to_hex_4bit(player["Overworld Sprite Palette"][2:]))

        return unitbase.replace(current_unitbase, new_unitbase, 1)

    def update_unitstat(player):
        new_unitstat = current_unitstat = unitstatarr[int(player["Player ID"])]
        
        new_unitstat = replace_hex(new_unitstat, iel.MIN_FP, num_to_hex_4bit(player["Min FP"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_TP, num_to_hex_4bit(player["Min TP"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_KICK, num_to_hex(player["Min Kick"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_BODY, num_to_hex(player["Min Body"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_CONTROL, num_to_hex(player["Min Control"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_GUARD, num_to_hex(player["Min Guard"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_SPEED, num_to_hex(player["Min Speed"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_STAMINA, num_to_hex(player["Min Stamina"]))
        new_unitstat = replace_hex(new_unitstat, iel.MIN_GUTS, num_to_hex(player["Min Guts"]))

        new_unitstat = replace_hex(new_unitstat, iel.FP, num_to_hex_4bit(player["FP"]))
        new_unitstat = replace_hex(new_unitstat, iel.TP, num_to_hex_4bit(player["TP"]))
        new_unitstat = replace_hex(new_unitstat, iel.KICK, num_to_hex(player["Kick"]))
        new_unitstat = replace_hex(new_unitstat, iel.BODY, num_to_hex(player["Body"]))
        new_unitstat = replace_hex(new_unitstat, iel.CONTROL, num_to_hex(player["Control"]))
        new_unitstat = replace_hex(new_unitstat, iel.GUARD, num_to_hex(player["Guard"]))
        new_unitstat = replace_hex(new_unitstat, iel.SPEED, num_to_hex(player["Speed"]))
        new_unitstat = replace_hex(new_unitstat, iel.STAMINA, num_to_hex(player["Stamina"]))
        new_unitstat = replace_hex(new_unitstat, iel.GUTS, num_to_hex(player["Guts"]))

        new_unitstat = replace_hex(new_unitstat, iel.FP_GROWTH, num_to_hex(player["FP Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.TP_GROWTH, num_to_hex(player["TP Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.KICK_GROWTH, num_to_hex(player["Kick Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.BODY_GROWTH, num_to_hex(player["Body Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.CONTROL_GROWTH, num_to_hex(player["Control Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.GUARD_GROWTH, num_to_hex(player["Guard Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.SPEED_GROWTH, num_to_hex(player["Speed Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.STAMINA_GROWTH, num_to_hex(player["Stamina Growth"]))
        new_unitstat = replace_hex(new_unitstat, iel.GUTS_GROWTH, num_to_hex(player["Guts Growth"]))

        new_unitstat = replace_hex(new_unitstat, iel.MOVE_1, to_hex_4bit(get_key(iedict.MOVES, player["Move 1"])[2:]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_2, to_hex_4bit(get_key(iedict.MOVES, player["Move 2"])[2:]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_3, to_hex_4bit(get_key(iedict.MOVES, player["Move 3"])[2:]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_4, to_hex_4bit(get_key(iedict.MOVES, player["Move 4"])[2:]))

        new_unitstat = replace_hex(new_unitstat, iel.MOVE_1_UNLOCK, num_to_hex(player["Move 1 Unlock"]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_2_UNLOCK, num_to_hex(player["Move 2 Unlock"]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_3_UNLOCK, num_to_hex(player["Move 3 Unlock"]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_4_UNLOCK, num_to_hex(player["Move 4 Unlock"]))

        new_unitstat = replace_hex(new_unitstat, iel.MOVE_1_LEVEL, num_to_hex(player["Move 1 Level"]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_2_LEVEL, num_to_hex(player["Move 2 Level"]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_3_LEVEL, num_to_hex(player["Move 3 Level"]))
        new_unitstat = replace_hex(new_unitstat, iel.MOVE_4_LEVEL, num_to_hex(player["Move 4 Level"]))
        
        new_unitstat = replace_hex(new_unitstat, iel.MAX_STATS, num_to_hex_4bit(player["Max Stats"]))

        return unitstat.replace(current_unitstat, new_unitstat, 1)
    
    def update_usearch(player):
        
        def get_key_binder():
            if get_key(iedict.LOCATIONS, player["Location/Team"]) != None:
                return get_key(iedict.LOCATIONS, player["Location/Team"])
            return get_key(iedict.BINDER_TEAM, player["Location/Team"])

        new_usearch = current_usearch = usearcharr[int(player["Binder ID"])]
        try:
            new_usearch = replace_hex(new_usearch, iel.BINDER_NICKNAME, fill_characters(from_text(player["Binder Nickname"]), 32))
            new_usearch = replace_hex(new_usearch, iel.RECRUITMENT_TYPE, get_key(iedict.RECRUITMENT_TYPE, player["Recruitment Type"]))
            new_usearch = replace_hex(new_usearch, iel.LOCATION, get_key_binder())

            return usearch.replace(current_usearch, new_usearch, 1)
        except:
            print(player, int(player["Binder ID"]), player["Binder Nickname"])
            exit()

    for player in data:
        unitbase = update_unitbase(player)
        unitstat = update_unitstat(player)
        usearch = update_usearch(player)
        
    with open('unitbase2.dat', 'wb') as f:
        f.write(bytes.fromhex(unitbase))

    with open('unitstat2.dat', 'wb') as f:
        f.write(bytes.fromhex(unitstat))

    with open('usearch2.dat', 'wb') as f:
        f.write(bytes.fromhex(usearch))