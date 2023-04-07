version = "0"

measurement_name = "xomdata"

type_of_db = 'influxdb'

server_address = {'dali':"90.147.119.208",'lngs':"127.0.0.1"}

database_list = ['influxdb', 'mongodb']

singularity_base = "singularity exec --bind /cvmfs/ --bind /project/ --bind /project2/ --bind /scratch/midway2/gaior --bind /dali /project2/lgrandi/xenonnt/singularity-images/"

configname = 'xomconfig.cfg'

figfolder = "/home/xom/data/v1.1/test/."

exec_period = 10

query_period = 100 # days period over which we should search in database (when xom will be running smoothly can beset to 1d)

output_folder = "/home/gaior/codes/xom/output/"

job_folder = output_folder + "/job_files/"

analysis_code_folder = "/home/gaior/codes/xom/backend/algorithms/"

container_path = "/project2/lgrandi/xenonnt/singularity-images/"

example_sub = "/home/gaior/codes/xom/utils/job_ex.sh"
