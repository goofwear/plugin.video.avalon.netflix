#cs ----------------------------------------------------------------------------

 AutoIt Version: 3.3.12.0
 Author:         iamdixon (avalonprojects.net)
 Date:           2014-10-28

 Script Function:
	Launch Netflix winPlayer (windows Netflix browser wrapper) and handle transition
	Between Netflix winPlayer and XBMC

#ce ----------------------------------------------------------------------------

; make sure we have some parameters (without a title id, there is nothing to play)
If $CmdLine[0] >= 1 Then
	; runup the winPlayer - passing the first command line argument as title id
	Run("WinPlayer\NetflixBrowser.exe " & $CmdLine[1])

	; minimize XBMC
	WinSetState("XBMC","",@SW_MINIMIZE)

	; setup a hotkey to close the player
	HotKeySet("{BACKSPACE}", "closeNetflixPlayer")
	; wait for the player to close
	ProcessWaitClose("NetflixBrowser.exe")

	; as long as we can assume we have correct command line parameters - launch series data updater.
	if $CmdLine[0] >= 5 Then
		Run("UpdateSeriesData.exe " & $CmdLine[2] & " " & $CmdLine[3] & " " & $CmdLine[4] & " " & $CmdLine[5], @SW_HIDE)
	EndIf

	; return to XBMC
	WinSetState("XBMC","",@SW_MAXIMIZE)
EndIf


;;; function to call from backspace hotkey
Func closeNetflixPlayer()
	; remove the hotkey listener
	HotKeySet("{BACKSPACE}")
	; close the winPlayer
	ProcessClose("NetflixBrowser.exe")
EndFunc