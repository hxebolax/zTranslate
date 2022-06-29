@cls
@echo off
scons --clean
git init
git add --all
git commit -m "Versión 0.1"
git push -u origin master
git push --tags
pause