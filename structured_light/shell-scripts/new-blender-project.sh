#!/bin/bash

#The script demonstrates the use of variables entered at the command line.
echo "My name is $1"
echo "I work for $2"

a="$../blender-projects"
echo "$a"

select dirname in ../blender-projects/*;
do
	echo "You selected $dirname ($REPLY)"
   echo "Enter project name"
   read projectName
   echo "$projectName"
   projectPath="${dirname}/${projectName}"
   echo "$projectPath"
   mkdir $projectPath
   imageFolder="images"
   



   break;
done
