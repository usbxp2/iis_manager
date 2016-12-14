#新建站点 api.dd.com，主机头为 api.dd.com，路经为 d:\apidd
New-Item iis:\Sites\%s -bindings @{protocol="http";bindingInformation=":%d:%s"} -physicalPath %s

#为站点 api.dd.com 更改应用程序池为 api.dd.com
Set-ItemProperty IIS:\Sites\%s -name applicationPool -value %s
