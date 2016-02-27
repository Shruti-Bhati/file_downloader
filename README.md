# file_downloader

USAGE

pydown.py - download file from a given url

DESCRIPTION

Downloads file from a given URL. The utility create separate processes and simulating multipart downloading. Each parallel chunk downloaded is 1000 bytes. It also supports resume functionality. If the file was partially downloaded previously, it resumes download from the previous point and doesn't start from scratch. If not destination is provided, the utility downloads in the same folder.utility by default creates a temp folder to download part of the file.The temp folder is deleted once the file download finishes. If the file download was interrupted, the temp folder is not destroyed.

EXAMPLES

pydown "http://abc.xyz.com/file.txt" "newfolder"
