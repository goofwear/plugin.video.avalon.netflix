#cs ----------------------------------------------------------------------------

 AutoIt Version: 3.3.12.0
 Author:         myName

 Script Function:
	Template AutoIt script.

#ce ----------------------------------------------------------------------------

; Script Start - Add your code below here

;MsgBox(4096, $CmdLine[0], 'Hi!')

Run("WinPlayer\NetflixBrowser.exe /movieid=" & $CmdLine[1])
WinSetState("XBMC","",@SW_MINIMIZE)


HotKeySet("{BACKSPACE}", "closeNetflixPlayer")
ProcessWaitClose("NetflixBrowser.exe")




Func closeNetflixPlayer()
	HotKeySet("{BACKSPACE}")
	WinSetState("XBMC","",@SW_MAXIMIZE)
	ProcessClose("NetflixBrowser.exe")
EndFunc