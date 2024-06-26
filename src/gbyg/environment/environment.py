from __future__ import annotations

import json

from .utils import *
from .tools import *

class Environment:
    def __init__(self, initial_environment_tree, agent_names:list[str], model_name:str|None = None):
        self._environment_tree = initial_environment_tree
        self._agent_names = agent_names

        self._action_target_selector = ActionTargetSelector(model_name)
        self._object_state_updater = ObjectStateUpdater(model_name)
        self._movement_detector = MovementActionDetector(model_name)
        self._object_mover = ObjectMover()
        self._observation_generator = ObservationGenerator(model_name)
        self._action_duration_estimator = ActionDurationEstimator(model_name)

    def step(self, agents_action:dict[str,str]) -> dict[str,dict[str,str]]:
        #Actions
        for agent in agents_action:
            environment = json.dumps(self._environment_tree)

            action = agents_action[agent]
            place = next(iter(get_object_room(self._environment_tree, agent).keys()))

            query = {'environment_tree':environment,
                    'actor':agent,
                    'place':place,
                    'action':action}
            target_result, _ = self._action_target_selector(query)

            for object_name in target_result["objects"]:
                place = next(iter(get_object_room(self._environment_tree, object_name).keys()))
                object_object = get_object(self._environment_tree, object_name)

                query = {'name':object_name,
                        'place':place,
                        'description':object_object["description"],
                        'state':object_object["state"],
                        'actor':agent,
                        'action':action}
                
                state_update, _ = self._object_state_updater(query)

                object_object["state"] = state_update["new_state"]

                environment = json.dumps(self._environment_tree)

        #Start observations
        observations = {}
        for agent in self._agent_names:
            observations[agent] = {}

        #Movements
        for agent in agents_action:
            action = agents_action[agent]
            
            query = {'agent':agent,"environment_tree":environment, 'action':action}
            detected_movement, _ = self._movement_detector(query)

            if detected_movement['is_movement']:
                query = {'object':agent,
                          'original_place':detected_movement["from"],
                          'target_place':detected_movement["to"],
                          'environment_tree':self._environment_tree}

                new_env, _ = self._object_mover(query)
                self._environment_tree = new_env["environment_tree"]

                observations[agent]["duration"] = detected_movement["movement_duration"]
            else:
                action_duration_result, _ = self._action_duration_estimator(query)
                observations[agent]["duration"]= action_duration_result["action_duration"]

        environment = json.dumps(self._environment_tree)

        #States and places
        for agent in self._agent_names:
            agent_room = get_object_room(self._environment_tree, agent)
            agent_object = get_object(agent_room, agent)
            
            observations[agent]["state"] = agent_object["state"]
            observations[agent]["place"] = next(iter(agent_room.keys()))

        #Observations
        for agent in self._agent_names:
            action = 'No action'
            if agent in agents_action:
                action = agents_action[agent]

            query = {'environment_tree':environment,
                    'agent':agent,
                    'state':observations[agent]["state"],
                    'place':observations[agent]["place"],
                    'action':action}

            observation_result, _ = self._observation_generator(query)

            observations[agent]["observation"] = observation_result["observation"]

        return observations