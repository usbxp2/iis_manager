#导入IIS管理模块
Import-Module WebAdministration

#新建应用程序池 {domain}
New-Item iis:\AppPools\%s
Set-ItemProperty iis:\AppPools\%s managedRuntimeVersion %s #更改应用程序池版本为v4.0，默认为v2.0（Windows Server 2008 R2）

