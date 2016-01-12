
@echo off
echo hi! this will test the neblina using test jig and a latero. 
echo Make sure the latero is connected to same network and it is connected to the test jig. 

:usrChoice
echo ========================
::echo 0. Execute all tests
echo 1. Execute Voltage test
echo 2. Fetch code and compile
echo 3. Program freescale
echo 4. Program RF (not implemented)
echo 5. Stream Test
set /p answer=e. Exit: 
if "%answer%"=="e" (exit)
if "%answer%"=="1" (GOTO vTest)
if "%answer%"=="2" (GOTO Compile)
if "%answer%"=="3" (GOTO ProgramFreescale)
if "%answer%"=="5" (GOTO StreamTest)
::if "%answer%"=="0" (GOTO All)

:All



:vTest
python neblina-latero-test.py %* || echo voltage test FAILED, check latero's ethernet connection
GOTO usrChoice

:Compile
::must add C:\Program Files (x86)\Git\bin to Environment Variables: PATH

cd C:\Users\Manou\Documents\GitHub\colibri
eval $(ssh-agent -s) || goto usrChoice
ssh-add /c/Users/Manou/.ssh/github_rsa
git pull origin master || goto usrChoice

 
"C:\eclipse\eclipsec.exe" --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data C:\Users\Manou\workspace.kinetis -cleanBuild CMSIS/Debug || echo compile CMSIS FAILED
"C:\eclipse\eclipsec.exe" --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data C:\Users\Manou\workspace.kinetis -cleanBuild colibri/Debug || echo compile colibri FAILED
"C:\eclipse\eclipsec.exe" --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data C:\Users\Manou\workspace.kinetis -cleanBuild NebKL26/Debug || echo compile NebKL26 FAILED
cd C:\Users\Manou\Documents\GitHub\neblina-python
GOTO usrChoice

:ProgramFreescale
set /p dummy=Make sure the programmer is properly connected to the freescale.
"C:\Program Files (x86)\GNU ARM Eclipse\openocd\bin\openocd.exe" -f "C:\Users\Manou\Dropbox\Neblina_Production\Firmware\KL26Z\kinetis.cfg" -c "program C:/Users/Manou/Documents/GitHub/colibri/Freescale/kl26z/apps/NebKL26/Debug/NebKL26.hex verify exit" || echo programming FAILED
GOTO usrChoice

:ProgramRF
set /p dummy=Make sure the programmer is properly connected to the nordic.

GOTO usrChoice

:StreamTest
del streamconfig.txt
python integrationTests.py %* || echo streaming test FAILED
GOTO usrChoice

