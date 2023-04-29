
# Espresso-Project Tester
Alternative phase 6 tester with (potentially unnecessary) additions that may make the main version confusing or bloated.

# Features: 
## Synchronous Testing
  > Forces each test to complete before another begins; No jumbled output
## User Specified File Ignorance: 
  > You can define a list of files in an external file to ignore in the case of known issues with the reference compiler.
#### Example: 
![Gyazo](https://i.gyazo.com/ca2db6f01c51d43ad20e77504324b9d9.png)
## Silent Compilation 
> Hides the extensive parser building stage outputting to the console, saves on space and focuses you to what's necessary!
## Single file checking 
  > Test a single file from the unit_tests folder without having to input the entire directory; will output the full diff 
### Usage: 
  ![Imgur](https://i.imgur.com/g6pLxWb.png)
### Example: 
 ![Imgur](https://i.imgur.com/m6Hlo3g.png)

## Multiple file checking 
>  Test all files from a single (or every) folder in unit_tests (default just Espresso) with options for Good and BadTests.
### Usage: 
   ![Imgur](https://i.imgur.com/idzkiem.png)
### Example: 
  ![Imgur](https://i.imgur.com/gBly5Ll.png)
  ![Imgur](https://i.imgur.com/umJZGez.png)

## Error handling and output
  > Catches erronous output; if a diff doesn't match, you'll know! 
### Example:
  ![Imgur](https://i.imgur.com/FeTpSWa.png)

## Seamless rechecking 
  > Failed file tests are stored in a secondary file, options allow for rechecking just these files specifically
### Output (failed.txt)
  ![Imgur](https://i.imgur.com/Ec4Ouyi.png)
### Example (partial):
  ![Imgur](https://i.imgur.com/vHC3cFA.png)
  
  ## In-depth help menus 
  > Confused? just add -h! 
  
  ![Imgur](https://i.imgur.com/t9yXCBe.png)

## Pre-Requisites

It is expected for this tester to be inside of this folder hierarchy: 
```
 ── parent_folder
    ├── unit_tests
    |   └── 6
    |	    ├── Espresso
    |	    |   └── *.java
    |	    ├── Espresso_Plus
    |	    |	└── *.java
    |	    └── Espresso_Star
    |		└── *.java
    ├── Phase6
    |	├── ./espressoc
    | 	└── ./espressocr
    └── tester.py

```

## Usage: 
To get you started: 

> cd into the parent folder 

`cd parent_folder`

> Clone the repository into the parent folder

`git clone https://github.com/heyitsmass/espresso-project-tester`

> Move the tester from the cloned repo folder into the parent folder

`mv ./espresso-project-tester/tester.py ../`

> Remove the unnecessary repo files

`rm -r espresso-project-tester/ --force`

> Run the tester

`python3 tester.py 6`

By default this will test every file inside of the `Espresso/GoodTests` folder and create a failed.txt file

## Exceptions: 

### Invalid Espressoc/Espressocr permissions: 
> Ensure ./espressoc and ./espressocr has appropriate permissions 
 #### Solution: 
 `cd Phase6 && chmod +x ./espressocr && chmod +x ./espressoc && cd -`
	
### Invalid tester permissions: 
>Ensure `tester.py` has appropriate permissions

#### Solution: 
`chmod +x tester.py`

### Overlapping filenames: 
>Ensure there does not exist the same filename inside of GoodTests and BadTests, if it does the full file path has to be specific; The script will output the potential file path for you if this happens. 
#### Example: 
```
> python3 tester.py 6 -c single Small.java
> Exception : Multiple file locations found for same file. Retry with exact filepath.
>             ./unit_tests/6/Espresso/GoodTests/Small.java or 
> 	      ./unit_tests/6/Espresso_Plus/BadTests/Small.java
```
#### Solution: 

`python3 tester.py 6 -c single ./unit_tests/6/Espresso/GoodTests/Small.java`

## Expected Workflow

The best way the use the script is to run the multiple tests using 

`python3 tester.py 6 -c --silent`

Then run any failed files individually, fixing the issues from that file (by default single is verbose)

`python3 tester.py 6 -c --silent single filename.java`

Then once fixing one (ideally multiple) retest the files in failed.txt

`python3 tester.py 6 -c --silent -r`

This will repopulate the failed.txt file and repeat until no files fail

## Usage Examples

Compile silently, test directories Espresso/GoodTests and Espresso/BadTests 

`python3 tester.py 6 -c --silent` 

\
Compile silently, test single file  

`python3 tester.py 6 -c --silent single small.java`

\
Test all GoodTest directories

`python3 tester.py 6 multiple -a -g`

\
Test star BadTest directories 

`python3 tester.py 6 multiple -s -b` 

\
Compile Silently, test plus GoodTest and BadTest directories with verbose output 

`python3 tester.py 6 -c -v --silent multiple -p -g -b` 


