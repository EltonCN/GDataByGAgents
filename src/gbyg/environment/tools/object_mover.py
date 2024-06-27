from __future__ import annotations

import warnings
from collections import deque

import toolpy as tp

class ObjectMover(tp.Tool):
    _description = "Moves a object from one room to another"
    _input_description = {'object':'name of the object beeing moved',
                          'original_place':'original place of the object',
                          'target_place':'new place of the object',
                          'environment_tree':'tree of the environment'}

    _return_description = {'environment_tree':'new tree of the environment'}

    def __init__(self) -> None:
        super().__init__(self._description, self._input_description)
    
    def _execute(self, query: dict[str, str] | None, context: str | None=None):
        object_name = query['object']
        original_place_name = query['original_place']
        target_place_name = query['target_place']
        environment_tree = query['environment_tree']

        if original_place_name == target_place_name:
            return {'environment_tree':environment_tree}, self._return_description

        #Search for the rooms:
        stack = deque()
        for room_name in environment_tree:
            if "object" in environment_tree[room_name]:
                continue

            stack.append([room_name, environment_tree[room_name]])

        origin_place : list = None
        target_place = None
        while len(stack) > 0 and (origin_place is None or target_place is None):
            room = stack.pop()
            room_name = room[0]
            sub_tree = room[1]

            if room_name == original_place_name:
                origin_place = sub_tree
            if room_name == target_place_name:
                target_place = sub_tree

            if isinstance(sub_tree, list):
                continue

            for subroom_name in sub_tree:
                stack.append([subroom_name, sub_tree[subroom_name]])

        for place in [origin_place, target_place]:
            if place is None:
                warnings.warn(f"Place {place} not found. Aborting change.")
                return {'environment_tree':environment_tree}, self._return_description 
            
        for index, origin_object in enumerate(origin_place):
            if origin_object["name"] == object_name:
                break
        else:
            origin_object = None

        if origin_object is None:
            warnings.warn(f"Origin object {object_name} not found in {original_place_name}. Aborting change.")
            return {'environment_tree':environment_tree}, self._return_description 
        
        del origin_place[index]

        target_place.append(origin_object)

        return {'environment_tree':environment_tree}, self._return_description 
