from __future__ import annotations

import toolpy as tp

class SoundSensor(tp.BasicTool):
    _description = ""
    _input_description = {}

    _system_message = '''You are a semantic sound sensor carried by a subject, that outputs in JSON. 
The JSON object must use the schema: {'sound_intensity':'float'}, where sound_intensity must be in dB.

Please use a valid JSON format.'''

    _base_prompt = '''Some sound intensity references:
0 dB: Threshold of human hearing
10 dB: Rustle of leaves
20 dB: Quiet room
60 dB: Normal conversation
70 dB: Busy street traffic
80 dB: Door slamming
90 dB: Loud car horn
100 dB: Loud siren
125 dB: Threshould of pain
160 dB: You just burst your eardrums

Generate a estimated sound intensity considering the perceptual information from our subject:

Subject current action: {action}
Subject current state: {state}
Subject observation: {observation}
'''

    _return_description = {'sound_intensity':'sensor sound intensity'}

    def __init__(self, model_name: str | None = None) -> None:
        super().__init__(description=self._description, 
                         input_description=self._input_description, 
                         prompt_template=self._base_prompt, 
                         return_description=self._return_description, 
                         system_message=self._system_message,
                         model_name=model_name,
                         json_mode=True)
        