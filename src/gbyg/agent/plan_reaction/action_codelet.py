from __future__ import annotations

import datetime
import json

import cst_python as cst

from .action_tool import ActionTool

class ActionCodelet(cst.Codelet):
    def __init__(self, 
                 agent_info_memory_name:str | None=None, 
                 agent_time_memory_name:str | None=None,
                 current_observation_name:str|None=None,
                 current_state_name:str|None=None, 
                 plan_memory_name:str|None = None,
                 know_world_name:str|None=None,
                 actual_place_name:str|None=None,
                 action_memory_name:str|None=None,
                 model_name:str|None=None) -> None:
        super().__init__()

        if agent_info_memory_name is None:
            agent_info_memory_name = "AgentInfo"
        if agent_time_memory_name is None:
            agent_time_memory_name = "AgentTime"
        if current_observation_name is None:
            current_observation_name = "CurrentObservation"
        if current_state_name is None:
            current_state_name = "CurrentState"
        if plan_memory_name is None:
            plan_memory_name = "Plan"
        if know_world_name is None:
            know_world_name = "KnowWorld"
        if actual_place_name is None:
            actual_place_name = "ActualPlace"
        if action_memory_name is None:
            action_memory_name = "Action"
        

        self._agent_info_memory_name = agent_info_memory_name
        self._agent_time_memory_name = agent_time_memory_name
        self._current_observation_name = current_observation_name
        self._current_state_name = current_state_name
        self._plan_memory_name = plan_memory_name
        self._know_world_name = know_world_name
        self._actual_place_name = actual_place_name
        
        self._action_memory_name = action_memory_name

        self._last_process = None
        self._current_action = ""

        self._action_tool = ActionTool(model_name)

    def access_memory_objects(self) -> None:
        self._agent_info_memory_mo = self.get_input(name=self._agent_info_memory_name)
        self._agent_time_memory_mo = self.get_input(name=self._agent_time_memory_name)
        self._current_observation_mo = self.get_input(name=self._current_observation_name)
        self._current_state_mo = self.get_input(name=self._current_state_name)
        self._plan_memory_mo = self.get_input(name=self._plan_memory_name)
        self._know_world_mo = self.get_input(name=self._know_world_name)
        self._actual_place_mo = self.get_input(name=self._actual_place_name)

        self._action_memory_mo = self.get_output(name=self._action_memory_name)

    def calculate_activation(self) -> None:
        pass

    def proc(self) -> None:
        agent_time = self._agent_time_memory_mo.get_info()

        if agent_time is None or agent_time == "":
            return

        if self._last_process is None:
            self._last_process = agent_time
        elif agent_time <= self._last_process:
            return
        
        self._last_process = agent_time

        plan = self._plan_memory_mo.get_info()

        if plan is None or plan == "":
            return

        agent_info = self._agent_info_memory_mo.get_info()

        know_world = json.dumps(self._know_world_mo.get_info())
        name = agent_info["name"]
        state = self._current_state_mo.get_info()
        observation = self._current_observation_mo.get_info()
        place = self._actual_place_mo.get_info()


        now = datetime.datetime.fromtimestamp(agent_time)
        current_action = ""
        next_action = plan[-1]
        for action in plan:
            action_time = datetime.datetime(now.year, now.month, now.day,
                                            action["hour"], action["minute"])
            
            if action_time < now:
                current_action = action
            else:
                next_action = action
                break
        
        if current_action != "":
            hour = current_action["hour"]
            minute = current_action["minute"]
            action_action = current_action["action"]
            current_action = f"{hour}:{minute}: {action_action}"

        hour = next_action["hour"]
        minute = next_action["minute"]
        action_action = next_action["action"]
        next_action = f"{hour}:{minute}: {action_action}"

        current_time = now.strftime("%H:%M")
        
        query = {"know_world_tree": know_world,
                "name": name,
                "state": state,
                "observation": observation,
                "place": place,
                "planned_action": current_action,
                "action": self._current_action,
                "next_action": next_action,
                "time": current_time}
        
        action_result, _ = self._action_tool(query)

        self._current_action = action_result["action"]
        self._action_memory_mo.set_info(self._current_action)
            
            
