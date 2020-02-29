from gym.envs.registration import register

register(id='SumoDuration-v0',
         entry_point='envs.sumo_envs:sumoDurationEnv'
         )
register(id='SumoProgram-v0',
         entry_point='envs.sumo_envs:sumoProgramEnv'
         )
