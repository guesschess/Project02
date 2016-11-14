#-*- coding: utf-8 -*-

import os, sys
import json
from pprint import pprint
import re
import csv


# the folder name
path = 'ca1/'

def parse(path):
    # returns a list containing the names of the entries in the directory given by path
    dirs = os.listdir(path)
    
    # used to store the file paths 
    file_paths = []
    
    # used to store the Appellate Court Docket Numbers
    doc_nums = []
    
    # to store Appellee
    case_names = []
    
    # store information of district court
    distr_cts = []
    
    # store information of district judge
    distr_judges = []
         
    #  all the files and directories
    for file in dirs:
        
        # join two strings in order to form the full filepath
        filepath = os.path.join(path, file)
        
        # store the full filepath into file_paths
        file_paths.append(filepath)
        
        
        # open every single json file
        with open(filepath) as infile:
             # only read first 1200 characters at a time
             info = infile.read(1200)
             
             # extract Appellate Court Docket Number: by searching of the case
             # for the pattern "No. ***-****"             
             ##doc_num = re.findall("No\.\s*\d*-\d+", info)            
             # store the docket numbers into doc_nums
             #doc_nums.append(doc_num)
             
             # extract the case name for the patten " **** v. ****"
             ##case_name = re.findall("([\w+\s]+,)(?:\W\w)+\s*Appellee,(?:\W\w)*\s*(v\.)(?:\W\w)*\s*([\w+\s]+,)", info)
             # store the case names into case_names
             #case_names.append(case_name)
             
             # extract district court info
             ##distr_ct = re.findall("FOR THE DISTRICT OF [\w+\s]+", info)
             # store the district courts into distr_cts
             #distr_cts.append(distr_ct)
            
             # extract district judges info for the pattern [***]
             brackets = re.findall("\[(.*?)\]", info)
             # extract only judges' names
             for i in range(0,len(brackets)):
                if "Judge" not in brackets[i]:
                    brackets[i] = " "
             distr_judges.append(brackets) 
             print distr_judges
             
                   
                    
                  
             
             
    result = zip(file_paths, distr_judges)
    ##print type(result)
             
    return result  
    

        
        

def main(): 
    result = parse(path)
    
    # first check whether a readable file exists or not
    flag = os.path.isfile('info.csv')
    # if it doesn't exist a csv file
    if not flag:
       print "Creating a new csv file..."
    # write extracted info into a csv file: "info.csv"
       with open('info.csv','w') as csvfile:
         
           # write extracted info into csv file
            writer = csv.writer(csvfile, dialect = 'excel')
            writer.writerows(result)
    else: print " just reading"
    
#     with open('ca1/1.json') as file:
#          info = file.read(2500)
#          print info


if __name__ == "__main__":
   main()
