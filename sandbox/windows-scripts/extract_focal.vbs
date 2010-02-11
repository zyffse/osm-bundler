' extract_focal.pl
'  -- Tool for preparing a directory of images for bundler by computing 
'     focal lengths from Exif tags
' Copyright 2005-2009 Noah Snavely

Dim BIN_PATH, JHEAD_EXE, ccd_widths, IMAGE_LIST, IMAGE_DIR
Dim num_output_images
Dim images()
Dim make, model, focal_mm, ccd_width_mm, res_x, res_y
Dim has_focal

BIN_PATH = Left(WScript.ScriptFullName, Len(WScript.ScriptFullName) - Len(WScript.ScriptName) - 1)
JHEAD_EXE = BIN_PATH & "\jhead.exe"
Const OUT_DIR = "prepare"
Const SCALE = 1.0

Const cameraFileName = "cameras.txt"

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = WScript.CreateObject("WScript.Shell")
Set cameraFile = fso.OpenTextFile(BIN_PATH & "\" &cameraFileName, 1)

' filling ccd_widths
Set ccd_widths = CreateObject("Scripting.Dictionary")
Do Until cameraFile.AtEndOfStream
    cameraLine = Split(cameraFile.ReadLine, vbTab)
    If Not ccd_widths.Exists(cameraLine(0)) Then
        ccd_widths.Add cameraLine(0), cameraLine(1)
    End If
Loop
cameraFile.Close

'mkdir $OUT_DIR
'rm -f $OUT_DIR/list.txt
If fso.FolderExists(OUT_DIR) Then
    If fso.FileExists(OUT_DIR+"\list.txt") Then
        fso.DeleteFile OUT_DIR+"\list.txt"
    End If 
Else
   fso.CreateFolder(OUT_DIR)
End If

IMAGE_LIST = ""
If WScript.Arguments.Count > 0 Then
    IMAGE_LIST = WScript.Arguments.Item(0)
End If

IMAGE_DIR = ""
If WScript.Arguments.Count > 1 Then
    IMAGE_DIR = WScript.Arguments.Item(1)
End If

WScript.Echo "Image list is " & IMAGE_LIST

' filling images array
imageCounter=0
If IMAGE_LIST = "" Then
    If IMAGE_DIR = "" Then IMAGE_DIR = shell.CurrentDirectory
    ' calculate number of jpeg files
    For Each fileObj In fso.GetFolder(IMAGE_DIR).Files
        If LCase(fso.GetExtensionName(fileObj.Path)) = "jpg" Then imageCounter = imageCounter + 1
    Next

    ' actually fill images array
    If imageCounter > 0 Then
        ReDim images(imageCounter-1)
        imageCounter=0
        For Each fileObj In fso.GetFolder(IMAGE_DIR).Files
            If LCase(fso.GetExtensionName(fileObj.Path)) = "jpg" Then
                images(imageCounter)=fileObj.Path
                imageCounter = imageCounter + 1
            End If
        Next
    End If
Else
    ' calculate number of jpeg files
    Set imageListFile = fso.OpenTextFile(IMAGE_LIST, 1)
    Do Until imageListFile.AtEndOfStream
        If imageListFile.ReadLine() <> "" Then imageCounter = imageCounter + 1
    Loop
    imageListFile.Close

    ' actually fill images array
    ReDim images(imageCounter-1)
    imageCounter=0
    Set imageListFile = fso.OpenTextFile(IMAGE_LIST, 1)
    Do Until imageListFile.AtEndOfStream
        imageLine = imageListFile.ReadLine()
        If imageLine <> "" Then
            If IMAGE_DIR = "" Then
                images(imageCounter) = imageLine
            Else
                images(imageCounter) = IMAGE_DIR & "\" & imageLine
            End If
            imageCounter = imageCounter + 1
        End If
    Loop
    imageListFile.Close
End If

' open result list.txt file for writing 
Set listFile = fso.CreateTextFile(OUT_DIR & "\list.txt")

num_output_images = 0
For Each img in images
    ccd_width_mm = 0
    res_x = 0
    WScript.Echo "[Extracting exif tags from image " & img &"]"
    ' run jhead.exe
    Set shellExec = shell.Exec("""" & JHEAD_EXE & """ """ & img & """")
    ' process exif lines
    exifLines=Split(shellExec.StdOut.ReadAll, vbNewLine)
    For Each exifLine in exifLines
        If exifLine <> "" Then
            colonPosition = InStr(exifLine, ":")
            If colonPosition > 0 Then
                ' grab pair attribute/value
                attribute = Trim(Left(exifLine, colonPosition-1))
                attributeValue = Trim(Right(exifLine, Len(exifLine)-colonPosition))
                Select Case attribute
                    Case "Camera make"
                        make = attributeValue
                    Case "Camera model"
                        model = attributeValue
                    Case "Focal length"
                        ' grab focal length
                        focal_mm = CDbl(Left(attributeValue, InStr(attributeValue, "mm")-1))
                        WScript.Echo "  [Focal length = " & focal_mm & "mm]"
                    Case "CCD width"
                        ' grab CCD width from exif
                        ccd_width_mm = CDbl(Left(attributeValue, InStr(attributeValue, "mm")-1))
                    Case "Resolution"
                        ' grab resolution
                        xPosition = InStr(attributeValue, "x")
                        res_x = CDbl(Left(attributeValue, xPosition-2))
                        res_y = CDbl(Right(attributeValue, Len(attributeValue)-xPosition-1))
                        WScript.Echo "  [Resolution = " & res_x & " x " & res_y & "]"
                End Select
            End If
        End If
    Next

    ' grab CCD width from ccd_widths Dictionary
    str = make & " " & model
    WScript.Echo ">" & str & "<"
    ' leading, trailing spaces have been already trimmed
    If ccd_widths.Exists(str) Then
        ccd_width_mm = ccd_widths.Item(str)
    Else
        WScript.Echo "[Couldn't find CCD width for camera " & str &"]"
        If ccd_width_mm <> 0 Then WScript.Echo "[Found in EXIF tags]"
    End If
    WScript.Echo "  [CCD width = " & ccd_width_mm &"mm]"
    
    If focal_mm = 0 Or ccd_width_mm = 0 Or res_x = 0 Then
	has_focal = False
    Else
	has_focal = True
    End If
    
    If res_x < res_y Then
	' aspect ratio is wrong
	tmp = res_x
	res_x = res_y
	res_y = tmp
    End If
    
    ' cut extension .jpg from the image file name
    basename = Left(img, Len(img)-4)

    If has_focal Then
	' compute focal length in pixels
	focal_pixels = res_x * (focal_mm / ccd_width_mm)
	WScript.Echo "  [Focal length (pixels) = " & focal_pixels & "]"
	line = img & " 0 " & SCALE * focal_pixels
    Else
	line = img
    End If
    
    listFile.WriteLine(line)
    num_output_images = num_output_images + 1
Next

WScript.Echo "[Found " & num_output_images & " good images]"