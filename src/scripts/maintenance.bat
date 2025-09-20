@echo off
echo Execution en tant que administrateur...

:: Vérifier s'il s'agit d'une élévation avec privilèges déjà enregistrés
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

:: Si l'erreur de cacls est 0 (pas d'erreur), alors nous avons déjà les privilèges administratifs.
if '%errorlevel%' == '0' goto :continue

:: Sinon, exécuter en tant qu'administrateur
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B

:continue
echo Execution en tant que administrateur reussie.

winget upgrade --all

echo Nettoyage et reparation en cour
cleanmgr

sfc /scannow

DISM /Online /Cleanup-Image /CheckHealth

DISM /Online /Cleanup-Image /ScanHealth

DISM /Online /Cleanup-Image /RestoreHealth