import gym
from gym.envs.registration import register

register(
    id="ElectroVoxel_2D-v0",
    entry_point="electrovoxel:ElectroVoxelenv",
)

env = gym.make('ElectroVoxel_2D-v0', render_mode="human")  

observation = env.reset()
for _ in range(50):
    env.render()
    # action = env.inc()  
    # observation, reward, done, info = env.step(action)
    # if done:
    #     observation = env.reset()
    observation = env.reset()
env.close()
