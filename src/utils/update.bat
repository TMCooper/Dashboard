@echo off
title Mise a jour du Dashboard

echo ===================================
echo  LANCEMENT DE LA MISE A JOUR AUTO
echo ===================================
echo.
echo Tentative de recuperation des dernieres modifications depuis le depot Git...
echo.

REM Execute la commande git pull pour mettre a jour les fichiers
git pull

echo.
echo =========================================================================
echo  MISE A JOUR TERMINEE !
echo.
echo  IMPORTANT: Si des fichiers du backend ont ete mis a jour,
echo  veuillez ARRETER et REDEMARRER l'application pour appliquer les changements.
echo =========================================================================
echo.
pause