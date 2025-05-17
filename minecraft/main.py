from utils.image_proc import thumbnail
from MinecraftQAGenerator import MinecraftQAGenerator
from tqdm import tqdm
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument('--num-per-question', type=int, required=True)
parser.add_argument('--out-dir', type=str, default='minecraft_dataset')
args = parser.parse_args()

output_dir = args.out_dir
num_per_question = args.num_per_question

generator  = MinecraftQAGenerator(
    output_dir=output_dir, space_ub=(3, 3, 4)
)

data = []

with tqdm(total=num_per_question * 5) as pbar:
    pbar.set_description('Generating scenery QA')
    for i in range(num_per_question):
        data.append(generator.gen_scenery_qa())
        pbar.update(1)
    pbar.set_description('Generating cube count QA')
    for i in range(num_per_question):
        data.append(generator.gen_cube_count_qa())
        pbar.update(1)
    pbar.set_description('Generating cross river QA')
    for i in range(num_per_question):
        data.append(generator.gen_cross_fluid_qa())
        pbar.update(1)
    pbar.set_description('Generating climb QA')
    for i in range(num_per_question):
        data.append(generator.gen_climb_qa())
        pbar.update(1)
    pbar.set_description('Generating cross river climb QA')
    for i in range(num_per_question):
        data.append(generator.gen_cross_river_climb_qa())
        pbar.update(1)
    pbar.set_description('Done')


print('Adjusting image sizes...')

for img_path in os.listdir(f'{output_dir}/images'):
    thumbnail(f'{output_dir}/images/{img_path}')

print('Done')

with open(f'{output_dir}/data.json', 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)