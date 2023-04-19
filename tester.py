import asyncio 
from pathlib import Path 
import subprocess 
import os 
import argparse 


parser = argparse.ArgumentParser()
parser.add_argument("phase", help="the current phase number.", type=int)

sub_parsers = parser.add_subparsers(title="actions")  

single_file_parser = sub_parsers.add_parser("single", help="Test a single file.") 
multi_file_parser = sub_parsers.add_parser("multiple", help="Test multiple files.") 
multi_file_parser.add_argument("-r", "--recheck", action="store_true", help="recheck the failed files outputted to failed.txt", required=False)
single_file_parser.add_argument("filename", help="The current file being scanned.", type=str) 

folder_group = multi_file_parser.add_mutually_exclusive_group() 

folder_group.add_argument("-p", "--plus", action="store_true", help="test plus files", required=False) 
folder_group.add_argument("-s", "--star", action="store_true", help="test star files", required=False)
folder_group.add_argument("-a" ,"--all", action="store_true", help="test all files", required=False) 

subfolder_group = multi_file_parser.add_mutually_exclusive_group()

subfolder_group.add_argument("-b", "--bad", action="store_true", help="test bad files", required=False) 
subfolder_group.add_argument("-g", "--good", action="store_true", help="test good files", required=False) 

compile_options = parser.add_argument_group() 

compile_options.add_argument("-c", "--compile", action="store_true", help="compile the program before running", required=False) 
compile_options.add_argument("--silent", action="store_true", help="compile silently", required=False)

parser.add_argument("-v", "--verbose", action="store_true", help="output diff info on failure.")
args = parser.parse_args()

import re 


async def test(file, phase, verbose=False): 
  project_dir = f"./Phase{phase}" 
  print(f"\033[33mTesting {file.name}:\033[0m", end="")
  with open('user', 'w') as user, open('ref', 'w') as ref: 
    subprocess.run(
      ['./espressoc', f"../{file}"], cwd=project_dir, stdout=user
    )

    subprocess.run(
      ['./espressocr', f'../{file}'], cwd=project_dir, stdout=ref
    )

    
    diff = subprocess.run(["diff", "-I", ".*: '.*'", "user", "ref"], stdout=subprocess.PIPE, encoding='utf8').stdout 


  if not diff: 
    print(f"\033[32m PASSED INITIAL CHECK\033[0m")
    try: 
      err_data = None
      with open('user', 'r') as ufile, open('ref', 'r') as rfile: 
        err_data = ufile.read()

        userFileData = re.split(r'-+\n', err_data)[2] 
        refFileData = re.split(r'-+\n', rfile.read())[2]


        userFiles = re.findall(r'\'((.+)[.](?:rj|j))\'', userFileData)
        refFiles = re.findall(r'\'((.+)[.](?:rj|j))\'', refFileData)
      
      for i, (userFilename, userBasename) in enumerate(userFiles): 
        refFilename, refBasename = refFiles[i]

        if userBasename != refBasename:
          raise Exception(f"{userFilename} does not match {refFilename}")

        print(f"\033[36mVerifying {userFilename}: \033[0m", end="")

        diff = subprocess.run(
          ["diff", userFilename, refFilename], 
          cwd=project_dir, 
          stdout=subprocess.PIPE
        ).stdout 

        if diff: 
          raise Exception(f"{userFilename} does not match {refFilename}.") 
        else: 
          print(f"\033[32m VALID\033[0m")
      
    except Exception as e: 
      print(f"\033[31mFILE VALIDATION FAILED \033[0m", end="")
      print(f":{e}" if verbose or args.verbose else '')

      if type(e) == IndexError:  
        print(f"\033[31mERROR IN MAIN FILE: \033[0m")
        print(err_data) 
        return file 
      
      if verbose or args.verbose: 
        subprocess.run(
          ["diff", "-y", userFilename, refFilename], 
          cwd=project_dir
        )
      pass 
      

  else: 
    print(f"\033[31m FAILED INITIAL CHECK\033[0m")
    if verbose or args.verbose: 
      subprocess.run(
        ["diff", "-y", "-t", "user", "ref"]
      )
    return file 


        
async def main(phase:int=1): 
  tests_dir = f"./unit_tests/{phase}/" 

  options = { 
    "plus" : ["_Plus"],
    "star": ["_Star"], 
    "all": ["", "_Plus", "_Star"], 
    "bad": ["BadTests"], 
    "good": ["GoodTests"]
  }

  failed = [] 

  item = [key for key, value in args._get_kwargs()]

  if 'compile' in item and args.compile:   
    if args.silent: 
      print("Silently compiling...")
      subprocess.run(["ant"], stdout=subprocess.PIPE, cwd=f"./Phase{args.phase}")
    else: 
      subprocess.run(["ant"], cwd=f"./Phase{args.phase}")
      
    print("Compiled.")

  if 'filename' not in item: 
    if 'recheck' in item and args.recheck: 
      print("Rechecking")
      try: 
        with open('failed.txt', 'r') as failedFile: 
          files = failedFile.readlines() 

          for file in files: 
            if file == '\n': continue 
            ret = await test(Path(file[:-1]), phase) 

            if ret: 
              failed.append(f"./{file}\n")

        with open('failed.txt', 'w') as file: 
          file.writelines(failed)  

      except FileNotFoundError as e: 
        print("Unable to find failed.txt, run initial tests first.")
        pass 

      return
      
    folders = [""]
    subfolders = ["GoodTests", "BadTests"] 

    for key, value in args._get_kwargs(): 
      if key in ['phase', 'compile', 'recheck', 'silent', 'verbose']: continue 
      if value: 
        if key in ["plus", "star", "all"]: 
          folders = options[key] 
        else: 
          subfolders = options[key] 
  
    for folder in folders:
      for subfolder in subfolders: 
        test_dir =  tests_dir + f'/Espresso{folder}/{subfolder}'

        files = Path(test_dir)

        print(f"\033[36mEspresso{folder}: \033[34m{subfolder}\033[0m")
        for f in sorted(files.iterdir()): 
          file = await test(f, phase) 

          if file: 
            failed.append(f"./{file}\n")
    
    with open('failed.txt', 'w') as file: 
      file.writelines(failed) 

  else: 

    file = None 
    if './unit_tests' in args.filename: 
      file = Path(args.filename) 


    if not file: 
      file_loc = ""

      for root, dirs, files in os.walk(tests_dir): 
        for file in files: 
          if file == args.filename: 
            if file_loc: 
              raise RuntimeError(f"Multiple file locations found for same file. Retry with exact filepath. \n\t{file_loc}, or \n\t{os.path.join(root, file)}")
             
            file_loc = os.path.join(root, file) 

      
      if not file_loc: 
        raise RuntimeError("Unable to find file.") 

      file = Path(file_loc) 


    await test(file, phase, True) 

if __name__ == "__main__": 

  asyncio.run(main(args.phase)) 

  
