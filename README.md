# epsonvt6_sim
github page: (https://github.com/gunnerdumas/epsonvt6_sim.git)


1) sim.launch.py
-before launching the sim.launch.py you need to first use xacro to build the epsonvt6.urdf file by hand as not automated yet.
-cd into the urdf folder and execute "xacro epsonvt6.urdf.xacro > epsonvt6.urdf".
-when launched a menu will appear prompting you for a world, select the empty one.

2) display.launch.py
-luanches rviz2 and a gui to control the epsonvt6 urdf model as well as display data