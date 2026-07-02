# TEST ONLY -- run via File > Scripting > Run Script File
# Tells us (1) is the script running, (2) do WinForms dialogs work,
# (3) are the schematic blocks actually present.

import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import MessageBox, OpenFileDialog, DialogResult

# 1) + 3): does a message box show, and how many systems exist?
names = []
try:
    for s in GetAllSystems():
        names.append(s.DisplayText)
except Exception, ex:
    names = ["<error: %s>" % ex]

MessageBox.Show("Script is running.\nSystems found (%d):\n%s"
                % (len(names), "\n".join(names)))

# 2): does a file-open dialog show at all (plain, main thread)?
d = OpenFileDialog()
d.Title = "TEST - pick any file (or Cancel)"
res = d.ShowDialog()
MessageBox.Show("Dialog result: %s\nFile: %s" % (res, d.FileName))
