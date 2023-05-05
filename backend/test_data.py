import strax
import straxen
import cutax
from argparse import ArgumentParser
import sys
sys.path +=['../utils/']
import utils
import constant

def main():
    parser = ArgumentParser()
    parser.add_argument('--excluded', nargs='+', type=str, default=[''])
    parser.add_argument('--included', nargs='+', type=str, default=[])
    parser.add_argument('--available', nargs='+', type=str, default=[])
    parser.add_argument('--analysis', type=str, default='')
    parser.add_argument('--container', type=str, default='')
    args = parser.parse_args()
    
    exclude_tags = args.excluded
    include_tags = args.included
    available_type = args.available
    analysis_name = args.analysis
    container = args.container
    

    print(container)
    print(analysis_name)
    print(exclude_tags)
    print(include_tags)
    print(available_type)


    #cluster='midway2'
    cluster='midway2'
    if cluster=='midway2':
        st = straxen.contexts.xenonnt_online(output_folder="/project2/lgrandi/xenonnt/processed/", _rucio_path=None)
    elif cluster=='dali':
        st = straxen.contexts.xenonnt_online()
    else:
        print('No valid cluster specified. Defaulting to dali options.')
        st = straxen.contexts.xenonnt_online()

    if available_type and include_tags:
        print("available and include tags")
        allruns = st.select_runs(available=available_type,
                                 exclude_tags=exclude_tags,
                                 include_tags=include_tags)
    elif available_type and not include_tags:
        print("available and not include tags")
        allruns = st.select_runs(available=available_type,
                                 exclude_tags=exclude_tags)

    else:
        print("not available and not include tags")
        allruns = st.select_runs(exclude_tags=exclude_tags)
    
    name_of_file = constant.availability_files_folder + analysis_name + "_" + container
    allruns.number.to_csv(name_of_file)

if __name__ == "__main__":
    main()
    
