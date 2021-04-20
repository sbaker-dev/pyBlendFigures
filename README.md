# pyBlendFigures
Making module adjustable figures with python and blender

## Install instructions

First you will need to have blender on your system which can be downloaded from [blender.org](https://www.blender.org/download/).
If you are working on a machine without install privileges, you can still use this package but you need to download the  
portable version. Blender and python are cross platform so can be used on Windows, MacOS and Linux, **however** it this
package has only been validated on Windows. 

Next you can pip install the package from PyPi via the command below. It is **strongly** recommended that you use a new
environment for this as this will help with the next step. 

```shell script
pip install pyBlendFigures
```

Navigate to your environment/Lib/site-packages and copy the contents of this folder, **not the site-packages folder
 itself**. Navigate to your blender install location, or were you downloaded it if you have the portable version, and
 then go into the version number(for example 2.83)/scripts/addons and paste the environment files. This will now mean 
 you have a working environment for you to pass commands to blender, and that blender has all the necessary support 
 libraries for it to run. 