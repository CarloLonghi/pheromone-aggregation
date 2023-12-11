import subprocess
import sys

if len(sys.argv) > 1:
    file_name = str(sys.argv[1])
else:
    print("File name set to default")
    file_name = "10gen_1"

sub = [
["python", "batch_run_strain_specific.py", file_name + "_strain_specific"],
["python", "batch_run_food_clustering.py",file_name+"_food_clustering"]
    ]

for i in range(len(sub)):
    print(f'Lauching process {i+1}/{len(sub)} - {sub[i][1]}')
    subprocess.run(sub[i])