!macro customInit
  ; Custom initialization for the NSIS installer
  
  ; Check for required Visual C++ Redistributable
  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" "Installed"
  ${If} $0 != "1"
    MessageBox MB_YESNO "Microsoft Visual C++ Redistributable 2015-2019 is required but not installed. Would you like to download and install it now?" IDYES installVCRedist IDNO skipVCRedist
    
    installVCRedist:
      ; Download and install VC++ Redistributable
      NSISdl::download "https://aka.ms/vs/16/release/vc_redist.x64.exe" "$TEMP\vc_redist.x64.exe"
      Pop $0
      ${If} $0 == "success"
        ExecWait '"$TEMP\vc_redist.x64.exe" /quiet /norestart' $0
        ${If} $0 != "0"
          MessageBox MB_OK "Failed to install Microsoft Visual C++ Redistributable. Please install it manually before running exo."
        ${EndIf}
        Delete "$TEMP\vc_redist.x64.exe"
      ${Else}
        MessageBox MB_OK "Failed to download Microsoft Visual C++ Redistributable. Please install it manually before running exo."
      ${EndIf}
    
    skipVCRedist:
  ${EndIf}
!macroend

!macro customInstall
  ; Custom installation steps for the NSIS installer
  
  ; Create a shortcut in the startup folder if requested
  ${If} ${SectionIsSelected} ${SecStartup}
    CreateShortCut "$SMSTARTUP\exo.lnk" "$INSTDIR\exo.exe"
  ${EndIf}
  
  ; Register protocol handler for exo://
  WriteRegStr HKCR "exo" "" "URL:exo Protocol"
  WriteRegStr HKCR "exo" "URL Protocol" ""
  WriteRegStr HKCR "exo\DefaultIcon" "" "$INSTDIR\exo.exe,0"
  WriteRegStr HKCR "exo\shell\open\command" "" '"$INSTDIR\exo.exe" "%1"'
!macroend

!macro customUnInstall
  ; Custom uninstallation steps for the NSIS installer
  
  ; Remove startup shortcut
  Delete "$SMSTARTUP\exo.lnk"
  
  ; Unregister protocol handler
  DeleteRegKey HKCR "exo"
!macroend
