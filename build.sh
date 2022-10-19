#!/bin/bash
touch bundle.py

cat signDetection.py > bundle.py
echo "" >> bundle.py
cat routines.py >> bundle.py
echo "" >> bundle.py
cat sensors.py >> bundle.py
echo "" >> bundle.py
# cat mapping.py >> bundle.py
# echo "" >> bundle.py
cat robot.py >> bundle.py
echo "" >> bundle.py
cat IFOS.py >> bundle.py
