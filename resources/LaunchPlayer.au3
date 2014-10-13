#cs ----------------------------------------------------------------------------

 AutoIt Version: 3.3.12.0
 Author:         myName

 Script Function:
	Template AutoIt script.

#ce ----------------------------------------------------------------------------

; Script Start - Add your code below here

;MsgBox(4096, "Args", $CmdLine[3])

;Run("WinPlayer\NetflixBrowser.exe /movieid=" & $CmdLine[1], "")
If $CmdLine[0] >= 1 Then
	Run("WinPlayer\NetflixBrowser.exe " & $CmdLine[1])
	WinSetState("XBMC","",@SW_MINIMIZE)


	HotKeySet("{BACKSPACE}", "closeNetflixPlayer")
	ProcessWaitClose("NetflixBrowser.exe")
	if $CmdLine[0] >= 5 Then
		Run("UpdateSeriesData.exe " & $CmdLine[2] & " " & $CmdLine[3] & " " & $CmdLine[4] & " " & $CmdLine[5])
	EndIf
	WinSetState("XBMC","",@SW_MAXIMIZE)
EndIf


Func closeNetflixPlayer()
	HotKeySet("{BACKSPACE}")
	
	ProcessClose("NetflixBrowser.exe")
EndFunc