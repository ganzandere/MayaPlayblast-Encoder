# MayaPlayblast-Encoder

`Python` `GUI` tool for `Autodesk Maya` that calls `playblast` by `maya.cmds` and sends completed frames directly to `FFmpeg.exe`.</br>
Has a cleanup switch that removes all intermediate images from the folder, after succesfully creating a video file.</br>
Currently only includes options for `libx264` and `libx265` encoders and few popular containers.