
@echo off
echo hi! this will test the neblina using test jig and a latero. 
echo Make sure the latero is connected to same network and it is connected to the test jig. 
if not exist %CD%\tempHexFolder (md %CD%\tempHexFolder)


:usrChoice
set alltest=0
echo =====================================
echo 0. Fetch code and compile latest code 
echo 1. Execute all tests
echo 2. Execute Voltage test
echo 3. Program freescale MCU
echo 4. Program nordic RF
echo 5. Stream Test
set /p answer=e. clean exit: 
if "%answer%"=="e" (GOTO iQuit)
if "%answer%"=="0" (GOTO Compile)
if "%answer%"=="1" (GOTO All)
if "%answer%"=="2" (GOTO vTest)
if "%answer%"=="3" (GOTO ProgramFreescale)
if "%answer%"=="4" (GOTO ProgramRF)
if "%answer%"=="5" (GOTO StreamTest)
GOTO usrChoice


:All
set alltest=1
GOTO vTest

:Compile ::these path are hard coded, would need to git pull into a temp folder and program hex.
"C:\Program Files\Git\git-bash.exe" runGitPullColibri.sh || ( echo Please install git bash & GOTO usrChoice )

"C:\eclipse\eclipsec.exe" --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data C:\Users\Manou\workspace.kinetis -cleanBuild CMSIS/Debug || (echo compile CMSIS FAILED & GOTO usrChoice)
"C:\eclipse\eclipsec.exe" --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data C:\Users\Manou\workspace.kinetis -cleanBuild colibri/Debug || (echo compile colibri FAILED & GOTO usrChoice)
"C:\eclipse\eclipsec.exe" --launcher.suppressErrors -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data C:\Users\Manou\workspace.kinetis -cleanBuild NebKL26/Debug || (echo compile NebKL26 FAILED & GOTO usrChoice)
copy "C:\Users\Manou\Dropbox\Neblina_Production\Firmware\KL26Z\kinetis.cfg" %CD%\tempHexFolder
copy "C:\Users\Manou\Documents\GitHub\colibri\Freescale\kl26z\apps\NebKL26\Debug\NebKL26.hex" %CD%\tempHexFolder
copy "C:\Users\Manou\Dropbox\Neblina_Production\Firmware\nRF51\s130_nrf51.hex" %CD%\tempHexFolder
copy "C:\Users\Manou\Dropbox\Neblina_Production\Firmware\nRF51\NebnRF51_v0_10.hex" %CD%\tempHexFolder\NebnRF51.hex
GOTO usrChoice

:vTest
python neblina-latero-test.py %* || echo voltage test FAILED, check latero's ethernet connection
if %alltest%==0 (GOTO usrChoice)


:ProgramFreescale
set /p dummy=Please connect the programmer to the Freescale MCU's jtag
cd %CD%\tempHexFolder
"C:\Program Files (x86)\GNU ARM Eclipse\openocd\bin\openocd.exe" -f "kinetis.cfg" -c "program NebKL26.hex verify exit" || echo programming FAILED
cd ..
if %alltest%==0 (GOTO usrChoice)

:ProgramRF
set /p dummy=Please connect the programmer to the Nordic RF's jtag
cd %CD%\tempHexFolder
"C:\Program Files (x86)\GNU ARM Eclipse\openocd\bin\openocd.exe" -f interface/cmsis-dap.cfg -f target/nrf51.cfg -c "program s130_nrf51.hex exit" || (echo programming FAILED & GOTO usrChoice)
"C:\Program Files (x86)\GNU ARM Eclipse\openocd\bin\openocd.exe" -f interface/cmsis-dap.cfg -f target/nrf51.cfg -c "program NebnRF51.hex exit" || echo programming FAILED
cd ..
if %alltest%==0 (GOTO usrChoice)

:StreamTest
python integrationTests.py %* || echo streaming test FAILED
GOTO usrChoice

:iQuit
taskkill /im ssh-agent.exe
if EXIST streamconfig.txt (del streamconfig.txt)
if EXIST  tempHexFolder (rd /S tempHexFolder)
exit

