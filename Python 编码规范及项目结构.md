深圳智裳科技  
林金壕 - 后端工程师  
2017年12月6日  


# Python 编码规范及项目结构
> 大部分源自 PEP8

## 编码规范：

1. 字符串统一使用单引号。	

	`'string'`	
2. 大括号，中括号，小括号之前不应使用空格。 	
 	`logger.info(list1[1])`		
3. 逗号，分号，冒号之前不应使用空格。	
 	`{'a': 1, 'b': 2, 'c': 3}`		
4. 在如下二元操作符左右使用单空格：	

	* 赋值： =		
	* 增量赋值： +=， -=		
	* 比较：==, <, >, !, in, is		
	* 布尔：and, or, no 	
	
	`a += 1`
5. 赋值号用在关键字参数和为默认参数时左右不使用空格	

	```
	def complex(real, imag=0):
	    return magic(r=real, i=imag)
	```

6. 命名规则：
	* 包名、模块名、局部变量名、函数名：全小写+下划线式驼峰
	
		`token_keeper`
	
	* 全局变量：全大写+下划线式驼峰
	
		`GLOBAL_VAR`
		
	* 类名：首字母大写式驼峰

		`ClassName()`
		
## 项目结构

```
.
├── run.py								# 项目启动文件
├── requirements.txt					
├── conf/								# 配置文件目录
├── dist/								# 项目压缩包目录
└── src/									
    ├── app.py							# app初始化
    ├── coroweb.py						# aiohttp封装
    ├── orm
    ├── config.py
    ├── main_app
    │   ├── resources/					# 静态资源
    │   ├── templates/					# 模板
    │   ├── models/						
    │   └── views/
    │       └── sub_view/
    │           └── view_apis.py		# 视图代码需要以view_开头
    └── sub_app							# 子项目
        ├── resources/					
        ├── templates/					
        ├── models/						
        └── views/
            └── sub_view/
                └── view_apis.py		# 视图代码需要以view_开头

```