try
	tell application "Finder" to set the currentFolder to (folder of the front window as alias)
on error
	set currentFolder to path to desktop folder as alias
end try

set nowSeconds to ((current date) - (date ("1/1/1970")) - (time to GMT)) as miles as string
set currentFile to POSIX path of currentFolder & "AAAAA_" & nowSeconds & ".txt"

do shell script "touch \"" & currentFile & "\""
-- do shell script "echo 'XXXXX' > \"" & currentFile & "\"" --
-- do shell script "touch ___NewFile.txt" --
-- do shell script "date >> \"" & currentFile & "\""--
