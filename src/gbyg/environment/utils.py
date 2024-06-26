from collections import deque

def get_object_room(environment_tree, object_name):
    stack = deque()
    for room_name in environment_tree:
        if "object" in environment_tree[room_name]:
            if environment_tree[room_name]["name"] == object_name:
                return environment_tree[room_name]
        else:
            stack.append([room_name, environment_tree[room_name]])

    origin_place : list = None
    target_place = None
    while len(stack) > 0 and (origin_place is None or target_place is None):
        room = stack.pop()
        room_name = room[0]
        sub_tree = room[1]

        if isinstance(sub_tree, list):
            for object in sub_tree:
                if object["name"] == object_name:
                    return {room_name: sub_tree}

        else:
            for subroom_name in sub_tree:
                stack.append([subroom_name, sub_tree[subroom_name]])

def get_object(environment_tree, object_name):
    stack = deque()
    for room_name in environment_tree:
        if "object" in environment_tree[room_name]:
            if environment_tree[room_name]["name"] == object_name:
                return environment_tree[room_name]
        else:
            stack.append([room_name, environment_tree[room_name]])

    origin_place : list = None
    target_place = None
    while len(stack) > 0 and (origin_place is None or target_place is None):
        room = stack.pop()
        room_name = room[0]
        sub_tree = room[1]

        if isinstance(sub_tree, list):
            for object in sub_tree:
                if object["name"] == object_name:
                    return object

        else:
            for subroom_name in sub_tree:
                stack.append([subroom_name, sub_tree[subroom_name]])