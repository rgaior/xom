import argparse

def main():
    parser = argparse.ArgumentParser("RunXom")
    parser.add_argument("runs", nargs='+',help="Run number to process")
    parser.add_argument("--test",help="Run number to process", action='store_true')
    args = parser.parse_args()    
    runs = args.runs
    for r in runs:        
        print(r)
    if args.test:
        print("test passed !")
    return runs
if __name__ == "__main__":
    main()

