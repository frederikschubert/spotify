#!/bin/zsh

#SBATCH --partition=gpu_cluster
#SBATCH --mail-type=ALL
#SBATCH --mail-user=schubert@tnt.uni-hannover.de
#SBATCH --time=7-0
#SBATCH --output=/home/schubert/projects/spotify/nobackup/slurm_logs/%x-%j.slurm.log
#SBATCH --export=ALL
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=5G
#SBATCH --gres=gpu:1


cd /home/schubert/projects/spotify
. /home/schubert/miniconda3/tmp/bin/activate spotify

srun $@