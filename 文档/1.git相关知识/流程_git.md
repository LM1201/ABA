#前置条件

+ 按照Git
+ 打开Git bash

#操作

##创建仓库
进入到所要创建 repository的地方，在Gitbash中输入
git init即可创建
.git是隐藏文件
里面包括：

		|   description 
		|   HEAD 
		|   config 
		|   批处理生成目录.bat 
		+---refs 
		|   +---heads 
		|   \---tags 
		+---hooks 
		|       applypatch-msg.sample 
		|       commit-msg.sample 
		|       post-update.sample 
		|       pre-applypatch.sample 
		|       pre-commit.sample 
		|       pre-push.sample 
		|       pre-rebase.sample 
		|       prepare-commit-msg.sample 
		|       update.sample 
		+---info 
		|       exclude 
		\---objects 
		    +---pack 
		    \---info 

hooks：存储钩子的文件夹
logs：存储日志的文件夹
refs：存储指向各个分支的指针（SHA-1标识）文件
objects：存放git对象
config：存放各种设置文档
HEAD：指向当前所在分支的指针文件路径，一般指向refs下的某文件

#增加文件

+ 创建文件
+ git add filename
+ git commit -m ""

git可以一次提交多个文件

#查看状态

git status

git diff
遇到一个问题：如何显示中文
方案1 
文件名乱码：git config --global core.quotepath false
https://gist.github.com/vkyii/1079783
 git config --global gui.encoding utf-8
方案2
https://gist.github.com/nightire/5069597
解决 Git 在 windows 下中文乱码的问题
方案3
 C:\Users\Administrator\.gitconfig

#git 用户名和邮箱配置
git config --global user.name "Your Name"
git config --global user.email "email@example.com"

git config --global --replace-all user.email "LM13241318304@gmail.com"


#查看日志
git log --pretty=oneline
