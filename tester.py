import asyncio 
from pathlib import Path 
import subprocess 
import os 
import argparse
import re 
import sys 

parser = argparse.ArgumentParser() 

parser.add_argument("phase", 
                    help="The current phase number.", 
                    type=int, default=6) 

subparsers = parser.add_subparsers(title="options") 

singleFileParser = subparsers.add_parser("single", help="Test a single file.") 
multiFileParser = subparsers.add_parser("multiple", help="Test multiple files.") 

singleFileParser.add_argument("filename", 
                              help="The current file being scanned.", 
                              type=str)

multiFileParser.add_argument("-r", "--recheck", 
                             help="Recheck the failed files outputted to failed.txt", 
                             action="store_true", required=False, default=False) 

folderGroup = multiFileParser.add_mutually_exclusive_group()

folderGroup.add_argument("-p", "--plus",
                         help="Test plus files.", 
                         action="store_true", required=False, default=False)
folderGroup.add_argument("-s", "--star", 
                         help="Test star files.", 
                         action="store_true", required=False, default=False)
folderGroup.add_argument("-a", "--all", 
                         help="Test all files.",
                         action="store_true", required=False, default=False)

subFolderGroup = multiFileParser.add_mutually_exclusive_group() 

subFolderGroup.add_argument("-b", "--bad",
                            help="Test bad files.",
                            action="store_true", required=False, default=False)
subFolderGroup.add_argument("-g", "--good", 
                            help="Test good files.", 
                            action="store_true", required=False, default=True)

compileOptions = parser.add_argument_group()

compileOptions.add_argument("-c", "--compile",
                            help="Compile the program before running.",
                            action="store_true", required=False, default=False)
compileOptions.add_argument("--silent", 
                            help="Compile silently.",
                            action="store_true", required=False, default=False)
parser.add_argument("-v", "--verbose", 
                    help="Output diff on failure.", 
                    action="store_true", required=False, default=False)

args = parser.parse_args()

def readData(filename:str): 

  """Read the lines of a file and return them as an array.

  Keyword arguments:
    filename -- the file being read 
  """
  with open(filename, 'r') as file: 
    return file.readlines() 

def writeData(data:list, filename:str): 
  """Write an array of data to a file.

  Keyword arguments:
    data -- list of data (strings) being written
    filename -- The file being written to
  """
  with open(filename, 'w') as file: 
    file.writelines(data) 


async def test(file:Path, verbose:bool=False): 
  """Test a single file

  Keyword arguments:
    file -- the file being tested
    verbose -- Determines verbosity of the output if args.verbose is not provided
  """

  projectDir = f"./Phase6" #The project dir 
  print(f"\033[33mTesting {file.name}:\033[0m", end="")
  with open('user', 'w') as user, open('ref', 'w') as ref:
    subprocess.run(
      ['./espressoc', f"../{file}"], cwd=projectDir, stdout=user  #Test against the user compiler
    )

    subprocess.run(
      ['./espressocr', f'../{file}'], cwd=projectDir, stdout=ref #Test against the ref compiler
    )

    #Run the diff check, ignore file names for now, they're always non-matching
    diff = subprocess.run(["diff", "-I", ".*: '.*'", "user", "ref"], 
                          stdout=subprocess.PIPE, encoding='utf8').stdout 

  if not diff: 
    print(f"\033[32m PASSED INITIAL CHECK\033[0m")

    try: 
      errData:str = None 
      with open('user', 'r') as user, open('ref', 'r') as ref: 
        # Store the file data incase an error is detected, it contains the message
        errData = user.read()  

        userFile = re.split(r'-+\n', errData)[2]  #Collect the filenames from the user output
        refFile = re.split(r'-+\n', ref.read())[2]  #Collect the filenames from the ref ouput

        #Seperate out the filenames and their base names
        userFiles = re.findall(r'\'((.+)[.](?:rj|j))\'', userFile)  
        refFiles = re.findall(r'\'((.+)[.](?:rj|j))\'', refFile)  

        #Iterate over the filenames
        for i, (userFileName, userBaseName) in enumerate(userFiles): 
          refFileName, refBaseName = refFiles[i] 

          if userBaseName != refBaseName: #Ensure the file names match before comparing
            raise NameError(f"{userFileName} does not match {refFileName}")
          
          print(f"\033[36mVerifying {userFileName}: \033[0m", end="")

          #Compare the user file and the reference file
          diff = subprocess.run(["diff", userFileName, refFileName], 
                                cwd=projectDir, 
                                stdout=subprocess.PIPE).stdout 
          if diff: 
            raise RuntimeError(f"{userFileName} does not match {refFileName}.")
          else:
            print(f"\033[32m VALID\033[0m")
    
    except Exception as err: 
      #Caught an exception in checking the files
      print(f"\033[31mFILE VALIDATION FAILED \033[0m", end="")
      print(f":{err}" if verbose or args.verbose else '')

      #We're missing filenames!?! Error in the test file (missing symbol or something)
      if type(err) == IndexError: 
        print(f"\033[31mERROR IN TEST FILE\033[0m")
        if verbose or args.verbose:
          print(f': {errData}') 
        return file 

      #We have file names but some file didn't validate.
      if verbose or args.verbose and type(err) != NameError: 
        subprocess.run(
          ["diff", "-y", userFileName, refFileName], 
          cwd=projectDir
        )

      pass 
  else: 
    #If we failed the initial check, output the diff if requested.
    print(f"\033[31m FAILED INITIAL CHECK\033[0m")
    if verbose or args.verbose: 
      subprocess.run(
        ["diff", "-y", "-t", "user", "ref"]
      )
    return file #reutrn the filename (failed) 

def compile(): 
  """Compiles the program"""
  if args.silent: 
    print("Silently Compiling...") 
    #PIPE the output to silently compile.
    subprocess.run(["ant"], stdout=subprocess.PIPE, cwd=f"./Phase6")
  else: 
    subprocess.run(["ant"], cwd=f"./Phase6")     

  print("Compiled.")
  
async def main(): 
  testsFolder = f"./unit_tests/{args.phase}/" #The unit_tests folder
  failedFiles:list[str] = [] #Any failed files

  #Potential options
  options = { 
    "plus" : ["_Plus"],
    "star": ["_Star"], 
    "all": ["", "_Plus", "_Star"], 
    "bad": ["BadTests"], 
    "good": ["GoodTests"] 
  }

  
  if 'filename' not in args: #Check multiple files 
    if 'recheck' in args and args.recheck: #Recheck the files in failed.txt
      print("Rechecking") 
      try: 

        files = readData("failed.txt") 
        if args.compile: 
          compile() 

        for file in files: 
          if file != '\n': 
            ret = await test(Path(file[:-1])) 

            if ret: 
              failedFiles.append(f"{file}") 
        
        writeData(failedFiles, "failed.txt") #Rewrite the failed files

      except FileNotFoundError as err: 
        print("Unable to find failed.txt, run initial tests first.") 
        return 
      
    else:
      folders = [""]  #Default Espresso folder
      subfolders = ["GoodTests"] #Default GoodTests Folder

      # Parse the args again... heh
      for key, value in args._get_kwargs(): 
        if key not in ['phase', 'compile', 'recheck', 'silent', 'verbose']: 
          if value: 
            if key in ["plus", "star", "all"]:
              folders = options[key] 
            else: 
              subfolders = options[key] 
     
      if args.compile: 
        compile() 

      # Grab all the files from our parsed options (in order) and test them
      try:
        for folder in folders: 
          for subfolder in subfolders: 
            testDir = testsFolder + f'/Espresso{folder}/{subfolder}'
            files = Path(testDir) 
            print(f"\033[36mEspresso{folder}: \033[34m{subfolder}\033[0m")
            for f in sorted(files.iterdir()): 
              file = await test(f) 
              if file: 
                failedFiles.append(f"./{file}\n")
      except FileNotFoundError as e: 
        print("ERROR: UNIT_TESTS FODLER DOES NOT EXIST") 
        return 
      
      writeData(failedFiles, "failed.txt")
  else: 
    #If we're testing a single file
    file = None

    if './unit_tests' in args.filename: 
      file = Path(args.filename) #If the full filepath was provided, test the file

    try: 
      if not file: #Otherwise walk the unit_tests directory and find the file
        fileLoc = ""
        for root, dirs, files in os.walk(testsFolder): 
          for f in files: 
            if f.lower() == args.filename.lower(): 
              if fileLoc: #We found multiple filenames
                raise RuntimeError(
                  f"Multiple file locations found for same file. Retry with exact filepath." +
                  f"\n\t{fileLoc}, or \n\t{os.path.join(root, f)}")
              else: 
                fileLoc = os.path.join(root, f)

        if not fileLoc: 
          raise RuntimeError("Unable to find file. (Invalid name?)")
        
        if args.compile: 
          compile() 

        file = Path(fileLoc)

        await test(file, True) #test the file
    except FileNotFoundError as e: 
      print("ERROR: UNIT_TESTS FODLER DOES NOT EXIST")
      return 

if __name__ == "__main__":

  if args.phase not in range(1, 7): 
    raise argparse.ArgumentTypeError("Maximum phase number is 6")

  if sys.version_info.minor < 7:  #Asyncio does not support .run() on python < 3.7 
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
  else: 
    asyncio.run(main())
