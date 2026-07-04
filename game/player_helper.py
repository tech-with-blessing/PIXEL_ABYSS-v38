from .assets import Assets

def remove(object_, id_):
    print(f"Removed player {id_}!")
    players = object_.players_config
    try:
        object_.players.remove(players[id_]['player'])
        object_._draw_list_dirty = True
        object_._entities_dirty = True

    except Exception as e:
        print(e)
        '''
        players[id_]['remove_player'].text = 'REMOVED'
        '''
        return

def save(object_, id_):
    print(f"Saved player {id_} settings!")
    players = object_.players_config
    object_.players_config[id_]['player'].name = players[id_]['player_type']
    object_.players_config[id_]['player'].color = players[id_]['player_color']
    object_.players_config[id_]['player'].personalise(2)

def change_color(object_, id_):
    print(f"Changed color for {id_}!")
    object_.players_config[id_]['player_color_num'] += 1

def change_type(object_, id_):
    print(f"Changed type for {id_}!")
    object_.players_config[id_]['player_type_num'] += 1

def back_(object_):
    print("Quit Player Edit!")
    object_.editing_player = False


layout = [
    (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06)
]

rel_rect = (0.5 - 0.1, 0.15, 0.2, 0.3)
